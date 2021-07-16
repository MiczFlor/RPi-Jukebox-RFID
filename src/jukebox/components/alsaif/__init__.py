import alsaaudio
import logging
import wave
import os
import jukebox.cfghandler
import jukebox.plugin as plugin

logger = logging.getLogger('jb.alsaif')
cfg = jukebox.cfghandler.get_handler('jukebox')


def clamp(n, minn, maxn):
    return min(max(n, minn), maxn)


# ---------------------------------------------------------------------------
# Volume Ctrl Service by ALSA
# ---------------------------------------------------------------------------


class AlsaCtrl:
    def __init__(self):
        mixer_name = cfg.setndefault('alsaif', 'mixer', value='Master')
        self.mixer = alsaaudio.Mixer(mixer_name, 0)

    def get_volume(self):
        return self.mixer.getvolume()[0]

    def set_volume(self, volume):
        logger.debug(f"Set Volume = {volume}")
        if not 0 <= volume <= 100:
            logger.warning(f"set_volume: volume out-of-range: {volume}")
            volume = clamp(volume, 0, 100)
        self.mixer.setvolume(volume)
        return self.get_volume()

    @plugin.tag
    def mute(self, mute_on=True):
        logger.debug(f"Set Mute = {mute_on}")
        self.mixer.setmute(1 if mute_on else 0)

    def unmute(self):
        self.mute(mute_on=False)

    def inc_volume(self, step=3):
        self.set_volume(self.get_volume() + step)

    def dec_volume(self, step=3):
        self.set_volume(self.get_volume() - step)


class AlsaCtrlBuilder:

    def __init__(self):
        self._instance = None

    def __call__(self, *args, **kwargs):
        if not self._instance:
            self._instance = AlsaCtrl()
        return self._instance


# ---------------------------------------------------------------------------
# Jingle Service for WAVE by ALSA
# ---------------------------------------------------------------------------

@plugin.register
class AlsaWave:
    fmt_lookup = {1: alsaaudio.PCM_FORMAT_U8,
                  2: alsaaudio.PCM_FORMAT_S16_LE,
                  3: alsaaudio.PCM_FORMAT_S24_3LE,
                  4: alsaaudio.PCM_FORMAT_S32_LE}

    @classmethod
    def _play_wave_core(cls, filename):
        with wave.open(filename, 'rb') as f:
            width = f.getsampwidth()
            if width not in AlsaWave.fmt_lookup:
                raise ValueError('Unsupported format')
            device_name = cfg.setndefault('alsaif', 'jingle_device', value='default')
            periodsize = f.getframerate() // 8
            device = alsaaudio.PCM(channels=f.getnchannels(),
                                   rate=f.getframerate(),
                                   format=AlsaWave.fmt_lookup[width],
                                   periodsize=periodsize,
                                   device=device_name)

            data = f.readframes(periodsize)
            while data:
                device.write(data)
                data = f.readframes(periodsize)

    def play(self, filename):
        if os.path.exists(filename) and os.path.isfile(filename):
            logger.debug("Playing wave file")
            try:
                AlsaWave._play_wave_core(filename)
            except Exception as e:
                logger.error(f"{type(e)}: {e}")
        else:
            logger.error(f"File does not exist: '{filename}'")
            raise KeyError(f"File does not exist: '{filename}'")


class AlsaWaveBuilder:

    def __init__(self):
        """
        Builder instantiates AlsaWave during init and not during first call because
        we want AlsaWave registers as plugin function in any case if this plugin is loaded
        (and not only on first use!)
        """
        self._instance = AlsaWave(plugin_name='alsawave', plugin_register=True)

    def __call__(self, *args, **kwargs):
        # if not self._instance:
        #     self._instance = AlsaWave(plugin_name='alsawave', plugin_register=True)
        return self._instance


# ---------------------------------------------------------------------------
# Plugin Initializer / Finalizer
# ---------------------------------------------------------------------------


def initialize():
    vmod = plugin.modules['volume']
    vmod.factory.register("alsa", AlsaCtrlBuilder())

    vmod = plugin.modules['jingle']
    vmod.factory.register("wav", AlsaWaveBuilder())
