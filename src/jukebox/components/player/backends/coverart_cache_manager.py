"""Cover-art cache support for the MPD backend."""

from mutagen.mp3 import MP3
from mutagen.id3 import ID3, APIC
from pathlib import Path
import hashlib
import logging
from queue import Queue
from threading import Thread
import jukebox.cfghandler

COVER_PREFIX = 'cover'
NO_COVER_ART_EXTENSION = 'no-art'
NO_CACHE = ''
CACHE_PENDING = 'CACHE_PENDING'
#: Bump whenever the cache key changes, so entries written by an older
#: version are purged instead of being served for the wrong audio file
CACHE_SCHEMA_VERSION = '2'
CACHE_SCHEMA_MARKER = '.cache-schema'

logger = logging.getLogger('jb.CoverartCacheManager')
cfg = jukebox.cfghandler.get_handler('jukebox')


class CoverartCacheManager:
    def __init__(self):
        coverart_cache_path = cfg.setndefault('webapp', 'coverart_cache_path', value='../../src/webapp/build/cover-cache')
        self.cache_folder_path = Path(coverart_cache_path).expanduser()
        try:
            self.cache_folder_path.mkdir(parents=True, exist_ok=True)
            self._migrate_cache()
        except OSError as e:
            logger.error(f"Could not prepare cover art cache folder {self.cache_folder_path}: {e}")
        self.write_queue = Queue()
        self.worker_thread = Thread(target=self.process_write_requests)
        self.worker_thread.daemon = True  # Ensure the thread closes with the program
        self.worker_thread.start()

    def generate_cache_key(self, cache_id: str) -> str:
        return f"{COVER_PREFIX}-{hashlib.sha256(cache_id.encode()).hexdigest()}"

    def get_cache_filename(self, mp3_file_path: str, cache_id: str) -> str:
        """Look up the cached cover art for an audio file

        :param mp3_file_path: Absolute path of the audio file, used to extract the cover art
        :param cache_id: Identifies the audio file uniquely within the library and is what the
            cache is keyed on: the path relative to the music library root, extension included.
            Keying on the bare filename would make every identically named track in the library
            share a single cover.
        """
        cache_key = self.generate_cache_key(cache_id)

        for path in self.cache_folder_path.iterdir():
            if path.stem == cache_key:
                if path.suffix == f".{NO_COVER_ART_EXTENSION}":
                    return NO_CACHE
                return path.name

        self.save_to_cache(mp3_file_path, cache_id)
        return CACHE_PENDING

    def save_to_cache(self, mp3_file_path: str, cache_id: str):
        self.write_queue.put((mp3_file_path, cache_id))

    def _save_to_cache(self, mp3_file_path: str, cache_id: str):
        cache_key = self.generate_cache_key(cache_id)

        file_extension, data = self._extract_album_art(mp3_file_path)
        if file_extension == NO_COVER_ART_EXTENSION:  # Check if cover has been added as separate file in folder
            file_extension, data = self._get_from_filesystem(mp3_file_path)

        cache_filename = f"{cache_key}.{file_extension}"
        full_path = self.cache_folder_path / cache_filename  # Works due to Pathlib

        with full_path.open('wb') as file:
            file.write(data)
            logger.debug(f"Created file: {cache_filename}")

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
            mp3_file_path, cache_id = self.write_queue.get()
            try:
                self._save_to_cache(mp3_file_path, cache_id)
            except Exception as e:
                logger.error(f"Error processing write request: {e}")
            self.write_queue.task_done()

    def _migrate_cache(self):
        """Purge cover files written with an outdated cache key"""
        marker = self.cache_folder_path / CACHE_SCHEMA_MARKER
        try:
            if marker.read_text().strip() == CACHE_SCHEMA_VERSION:
                return
        except OSError:
            pass  # No marker yet: the cache predates the schema version

        logger.info("Cover art cache key changed, purging stale entries")
        self._purge_cover_files()
        marker.write_text(CACHE_SCHEMA_VERSION)

    def _purge_cover_files(self):
        """Delete the cached covers, leaving bookkeeping files like the schema marker in place"""
        for path in self.cache_folder_path.glob(f'{COVER_PREFIX}-*'):
            if path.is_file():
                path.unlink()
                logger.debug(f"Deleted cached file: {path.name}")

    def flush_cache(self):
        self._purge_cover_files()
        logger.info("Cache flushed successfully.")
