import os
import jukebox.cfghandler

cfg = jukebox.cfghandler.get_handler('jukebox')


class CoverartCacheManager:
    def __init__(self):
        coverart_cache_path = cfg.setndefault('webapp', 'coverart_cache_path', value='../../src/webapp/build/cover-cache')
        self.cache_folder_path = os.path.expanduser(coverart_cache_path)

    def find_file_by_hash(self, hash_value):
        for filename in os.listdir(self.cache_folder_path):
            if filename.startswith(hash_value):
                return filename
        return None

    def save_to_cache(self, base_filename, album_art_data):
        mime_type = album_art_data['type']
        file_extension = 'jpg' if mime_type == 'image/jpeg' else mime_type.split('/')[-1]
        cache_filename = f"{base_filename}.{file_extension}"

        with open(os.path.join(self.cache_folder_path, cache_filename), 'wb') as file:
            file.write(album_art_data['binary'])

        return cache_filename
