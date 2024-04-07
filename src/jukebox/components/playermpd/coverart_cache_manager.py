from pathlib import Path
import hashlib
import logging
import jukebox.cfghandler

NO_COVER_ART_EXTENSION = 'no-art'
NO_CONTENT = ''
NOT_CACHED = None

logger = logging.getLogger('jb.CoverartCacheManager')
cfg = jukebox.cfghandler.get_handler('jukebox')


class CoverartCacheManager:
    def __init__(self):
        coverart_cache_path = cfg.setndefault('webapp', 'coverart_cache_path', value='../../src/webapp/build/cover-cache')
        self.cache_folder_path = Path(coverart_cache_path).expanduser()

    def generate_cache_key(self, base_filename: str) -> str:
        return f'cover-{hashlib.sha256(base_filename.encode()).hexdigest()}'

    def find_file_by_hash(self, base_filename: str) -> str:
        cache_key = self.generate_cache_key(base_filename)
        for path in self.cache_folder_path.iterdir():
            if path.stem == cache_key:
                if path.suffix == f'.{NO_COVER_ART_EXTENSION}':
                    return NO_CONTENT
                return path.name
        return NOT_CACHED

    def save_to_cache(self, base_filename: str, album_art_data: dict) -> str:
        cache_key = self.generate_cache_key(base_filename)
        file_extension = NO_COVER_ART_EXTENSION
        data = b''

        if album_art_data:
            mime_type = album_art_data.get('type', 'image/jpeg')
            file_extension = 'jpg' if mime_type == 'image/jpeg' else mime_type.split('/')[-1]
            data = album_art_data.get('binary', b'')

        cache_filename = f"{cache_key}.{file_extension}"
        logger.debug(f'Created file: {cache_filename}')
        full_path = self.cache_folder_path / cache_filename

        with full_path.open('wb') as file:
            file.write(data)

        return cache_filename if data else NO_CONTENT
