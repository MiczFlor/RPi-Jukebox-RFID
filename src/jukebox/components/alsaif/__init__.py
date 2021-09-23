"""ALSA Volume Control Plugin Package for volume.VolumeFactory

References:
https://larsimmisch.github.io/pyalsaaudio/index.html
https://github.com/larsimmisch/pyalsaaudio/
"""
import alsaaudio
import logging
import jukebox.cfghandler
import jukebox.plugs as plugin

logger = logging.getLogger('jb.alsaif')
cfg = jukebox.cfghandler.get_handler('jukebox')


def clamp(n, minn, maxn):
    return min(max(n, minn), maxn)


# ---------------------------------------------------------------------------
# Volume Ctrl Service by ALSA
# ---------------------------------------------------------------------------


class AlsaCtrl:
    """ALSA Volume Control"""

    def __init__(self):
        mixer_name = cfg.setndefault('alsaif', 'mixer', value='Master')
        self.mixer = alsaaudio.Mixer(mixer_name, 0)

    @plugin.tag
    def get_volume(self):
        return self.mixer.getvolume()[0]

    @plugin.tag
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
        # TODO: try-block as not all mixers have mute capability
        self.mixer.setmute(1 if mute_on else 0)

    @plugin.tag
    def unmute(self):
        self.mute(mute_on=False)

    @plugin.tag
    def inc_volume(self, step=3):
        return self.set_volume(self.get_volume() + step)

    @plugin.tag
    def dec_volume(self, step=3):
        return self.set_volume(self.get_volume() - step)


class AlsaCtrlBuilder:

    def __init__(self):
        self._instance = None

    def __call__(self, *args, **kwargs):
        if not self._instance:
            self._instance = AlsaCtrl()
        return self._instance


# ---------------------------------------------------------------------------
# Plugin Initializer / Finalizer
# ---------------------------------------------------------------------------

@plugin.initialize
def initialize():
    volume = plugin.get('volume')
    volume.factory.register("alsa", AlsaCtrlBuilder())
