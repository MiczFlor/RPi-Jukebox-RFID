"""
Read all cover art from music save it to a cache for the UI to load
"""

import os
from base64 import b64encode
import eyed3
import logging
import jukebox.cfghandler
import jukebox.plugs as plugin
import components.player

logger = logging.getLogger('jb.music_cover_art')
cfg = jukebox.cfghandler.get_handler('jukebox')


class MusicCoverArt:
    def __init__(self):
        self.music_library_path = components.player.get_music_library_path()

        if self.music_library_path is None:
            logger.error("Missing config, can't initialize plugin")

    @plugin.tag
    def get_by_filename_as_base64(self, audio_src: str):
        cover_base64_string = ''

        audio_file_path = ''
        try:
            audio_file_path = os.path.join(self.music_library_path, audio_src)
            file_data = eyed3.load(audio_file_path)
        except Exception as e:
            logger.error(f"ERROR {e.__class__.__name__}: {e} for music_library_path="
                         f"'{self.music_library_path}', audio_src='{audio_src}'")
            return cover_base64_string

        try:
            # Take the first image, if multiple images are embedded
            image = file_data.tag.images.__iter__().__next__()
        except StopIteration:
            # TODO: check if folder.jpg exists?
            pass
        else:
            cover_encoded_base64_bytes = b64encode(image.image_data)
            cover_base64_string = cover_encoded_base64_bytes.decode('utf-8')

        return cover_base64_string


@plugin.initialize
def initialize():
    music_cover_art = MusicCoverArt()
    plugin.register(music_cover_art, name='ctrl')
