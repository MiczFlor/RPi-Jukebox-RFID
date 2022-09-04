"""
Read all cover art from music save it to a cache for the UI to load

.. note:: Not implemented. This is a feature planned for a future release.
"""
import logging
import jukebox.cfghandler
import jukebox.plugs as plugin
import components.playern.backends.mpd.musiclib

logger = logging.getLogger('jb.music_cover_art')
cfg = jukebox.cfghandler.get_handler('jukebox')


class MusicCoverArt:
    def __init__(self):
        self.music_library_path = components.playern.backends.mpd.musiclib.get_music_library_path()

        if self.music_library_path is None:
            logger.error("Missing config, can't initialize plugin")

    @plugin.tag
    def get_by_filename_as_base64(self, audio_src: str):
        """
        Not implemented. This is a feature planned for a future release.
        """
        cover_base64_string = ''
        return cover_base64_string


@plugin.initialize
def initialize():
    music_cover_art = MusicCoverArt()
    plugin.register(music_cover_art, name='ctrl')
