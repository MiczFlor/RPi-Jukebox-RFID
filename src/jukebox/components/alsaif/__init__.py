# -*- coding: utf-8 -*-
import alsaaudio
import logging
from functools import partial
import wave
import jukebox.cfghandler
import jukebox.plugin as plugin
import os

logger = logging.getLogger('jb.alsaif')
cfg = jukebox.cfghandler.get_handler('jukebox')


def clamp(n, minn, maxn):
    return min(max(n, minn), maxn)


@plugin.register
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

    def mute(self, mute_on=True):
        logger.debug(f"Set Mute = {mute_on}")
        self.mixer.setmute(1 if mute_on else 0)

    def unmute(self):
        self.mute(mute_on=False)

    def inc_volume(self, step=3):
        self.set_volume(self.get_volume() + step)

    def dec_volume(self, step=3):
        self.set_volume(self.get_volume() - step)


def _play_wave_core(filename):
    with wave.open(filename, 'rb') as f:
        width = f.getsampwidth()
        fmt_lookup = {1: alsaaudio.PCM_FORMAT_U8,
                      2: alsaaudio.PCM_FORMAT_S16_LE,
                      3: alsaaudio.PCM_FORMAT_S24_3LE,
                      4: alsaaudio.PCM_FORMAT_S32_LE}
        if width not in fmt_lookup:
            raise ValueError('Unsupported format')
        device_name = cfg.setndefault('alsaif', 'start_sound_device', value='default')
        periodsize = f.getframerate() // 8
        device = alsaaudio.PCM(channels=f.getnchannels(),
                               rate=f.getframerate(),
                               format=fmt_lookup[width],
                               periodsize=periodsize,
                               device=device_name)

        data = f.readframes(periodsize)
        while data:
            device.write(data)
            data = f.readframes(periodsize)


@plugin.register
def play_wave(filename):
    if os.path.exists(filename) and os.path.isfile(filename):
        logger.debug("Playing wave file")
        try:
            _play_wave_core(filename)
        except Exception as e:
            logger.error(f"{type(e)}: {e}")
    else:
        logger.error(f"File does not exist: '{filename}'")
        raise KeyError(f"File does not exist: '{filename}'")


# ---------------------------------------------------------------------------
# Module interface API for jukebox
# ---------------------------------------------------------------------------


alsactrl = None


def init():
    global alsactrl
    try:
        alsactrl = AlsaCtrl(plugin_name='ctrl')
    except Exception as e:
        logger.error("Failed to init AlsaCtrl. Trying without...")
        logger.error(f"Reason: {e}")
