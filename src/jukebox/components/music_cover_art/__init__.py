"""
Read all cover art from music save it to a cache for the UI to load
"""

from base64 import b64encode
import eyed3
import logging
from pathlib import Path
import jukebox.cfghandler
import jukebox.plugs as plugin
import jukebox.publishing as pub
from jukebox.publishing.subscriber import Subscriber

logger = logging.getLogger('jb.music_cover_art')
cfg = jukebox.cfghandler.get_handler('jukebox')

class MusicCoverArt:
    def __init__(self):
        self.audiofolder_path = cfg.getn('system', 'audiofolder_path')

        if self.audiofolder_path is None or self.cache_path is None:
            logger.error("Missing config, can't initialize plugin")

    @plugin.tag
    def get_by_filename_as_base64(self, audio_src):
        cover_base64_string = ''

        try:
            audio_file_path = self.audiofolder_path + '/' + audio_src
            file_data = eyed3.load(audio_file_path)
        except Exception as e:
            logger.error(f'File does not exist: {e}')
            return cover_base64_string

        for image in file_data.tag.images:
            cover_encoded_base64_bytes = b64encode(image.image_data)
            cover_base64_string = cover_encoded_base64_bytes.decode('utf-8')

        return cover_base64_string

    @plugin.tag
    def get_by_folder_name_as_base64(self, folder):
        # Find first file in folder
        os.listdir(path)[0]

    # Currently not used, but left here for
    def save_to_cache(self, file_name, file_data):
        cache_path = self.cache_path

        if cache_path is None:
            return

        Path(cache_path).mkdir(parents=True, exist_ok=True)
        cache_path_file = cache_path + '/' + file_name

        if Path(cache_path_file).exists() is not True:
            try:
                image_file = open(cache_path_file, 'wb')
                image_file.write(file_data)
                image_file.close()
                logger.debug('Write file: ' + cache_path_file)
            except Exception as e:
                logger.error(f'Error while storing to cache: {e}')


# # The initializer stuff gets executed directly
music_cover_art = MusicCoverArt()
plugin.register(music_cover_art, name='ctrl')
