from mutagen.mp3 import MP3
from mutagen.id3 import ID3, APIC
from pathlib import Path
import hashlib
import logging
from queue import Queue
from threading import Thread, Lock
import jukebox.cfghandler

COVER_PREFIX = 'cover'
NO_COVER_ART_EXTENSION = 'no-art'
NO_CACHE = ''
CACHE_PENDING = 'CACHE_PENDING'

logger = logging.getLogger('jb.CoverartCacheManager')
cfg = jukebox.cfghandler.get_handler('jukebox')


class CoverartCacheManager:
    def __init__(self):
        coverart_cache_path = cfg.setndefault('webapp', 'coverart_cache_path', value='../../src/webapp/build/cover-cache')
        self.cache_folder_path = Path(coverart_cache_path).expanduser()
        # In-memory index (cache_key -> filename) so a lookup is a dict access instead of
        # re-listing and comparing against every file in the cache folder on every single
        # coverart request. That linear scan was cheap for a handful of files, but with a
        # library of any real size (called once per song/album shown in the WebUI) it turned
        # into a steady, significant CPU cost - see the WebUI-hang investigation.
        self._index_lock = Lock()
        self._cache_index = {}
        self._build_cache_index()
        self.write_queue = Queue()
        self.worker_thread = Thread(target=self.process_write_requests)
        self.worker_thread.daemon = True  # Ensure the thread closes with the program
        self.worker_thread.start()

    def _build_cache_index(self):
        self.cache_folder_path.mkdir(parents=True, exist_ok=True)
        for path in self.cache_folder_path.iterdir():
            if path.is_file():
                self._cache_index[path.stem] = path.name

    def generate_cache_key(self, base_filename: str) -> str:
        return f"{COVER_PREFIX}-{hashlib.sha256(base_filename.encode()).hexdigest()}"

    def get_cache_filename(self, mp3_file_path: str) -> str:
        base_filename = Path(mp3_file_path).stem
        cache_key = self.generate_cache_key(base_filename)

        with self._index_lock:
            cached_name = self._cache_index.get(cache_key)

        if cached_name is not None:
            if cached_name.endswith(f".{NO_COVER_ART_EXTENSION}"):
                return NO_CACHE
            return cached_name

        self.save_to_cache(mp3_file_path)
        return CACHE_PENDING

    def save_to_cache(self, mp3_file_path: str):
        self.write_queue.put(mp3_file_path)

    def _save_to_cache(self, mp3_file_path: str):
        base_filename = Path(mp3_file_path).stem
        cache_key = self.generate_cache_key(base_filename)

        file_extension, data = self._extract_album_art(mp3_file_path)
        if file_extension == NO_COVER_ART_EXTENSION:  # Check if cover has been added as separate file in folder
            file_extension, data = self._get_from_filesystem(mp3_file_path)

        cache_filename = f"{cache_key}.{file_extension}"
        full_path = self.cache_folder_path / cache_filename  # Works due to Pathlib

        with full_path.open('wb') as file:
            file.write(data)
            logger.debug(f"Created file: {cache_filename}")

        with self._index_lock:
            self._cache_index[cache_key] = cache_filename

        return cache_filename

    def _extract_album_art(self, mp3_file_path: str) -> tuple:
        try:
            audio_file = MP3(mp3_file_path, ID3=ID3)
        except Exception as e:
            logger.error(f"Error reading MP3 file {mp3_file_path}: {e}")
            return (NO_COVER_ART_EXTENSION, b'')

        for tag in audio_file.tags.values():
            if isinstance(tag, APIC):
                if tag.mime and tag.data:
                    file_extension = 'jpg' if tag.mime == 'image/jpeg' else tag.mime.split('/')[-1]
                    return (file_extension, tag.data)

        return (NO_COVER_ART_EXTENSION, b'')

    def _get_from_filesystem(self, mp3_file_path: str) -> tuple:
        path = Path(mp3_file_path)
        directory = path.parent
        cover_files = list(directory.glob('Cover.*')) + list(directory.glob('cover.*'))

        for file in cover_files:
            if file.suffix.lower() in ['.jpg', '.jpeg', '.png']:
                with file.open('rb') as img_file:
                    data = img_file.read()
                    file_extension = file.suffix[1:]  # Get extension without dot
                    return (file_extension, data)

        return (NO_COVER_ART_EXTENSION, b'')

    def process_write_requests(self):
        while True:
            mp3_file_path = self.write_queue.get()
            try:
                self._save_to_cache(mp3_file_path)
            except Exception as e:
                logger.error(f"Error processing write request: {e}")
            self.write_queue.task_done()

    def flush_cache(self):
        for path in self.cache_folder_path.iterdir():
            if path.is_file():
                path.unlink()
                logger.debug(f"Deleted cached file: {path.name}")
        with self._index_lock:
            self._cache_index.clear()
        logger.info("Cache flushed successfully.")
