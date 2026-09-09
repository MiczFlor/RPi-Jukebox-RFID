from pathlib import Path
from queue import Queue

import pytest

from components.player.backends.coverart_cache_manager import (
    CACHE_PENDING,
    CACHE_SCHEMA_MARKER,
    CACHE_SCHEMA_VERSION,
    NO_CACHE,
    NO_COVER_ART_EXTENSION,
    CoverartCacheManager,
)


# Two audiobooks ripped by the same tool, so both use the publisher's chapter naming
BOOK_A = 'Marc-Uwe Kling - Das NEINhorn/1-01 Kapitel 1.mp3'
BOOK_B = 'Marc-Uwe Kling - Das NEINhorn und die SchLANGEWEILE/1-01 Kapitel 1.mp3'

ARTWORK = {
    BOOK_A: b'\xff\xd8\xff' + b'A' * 200,
    BOOK_B: b'\xff\xd8\xff' + b'B' * 400,
}


def cache_manager(cache_folder: Path) -> CoverartCacheManager:
    """Build a manager without its config handler, cache migration and worker thread"""
    manager = CoverartCacheManager.__new__(CoverartCacheManager)
    manager.cache_folder_path = cache_folder
    manager.write_queue = Queue()
    return manager


@pytest.fixture
def cache_folder(tmp_path):
    folder = tmp_path / 'cover-cache'
    folder.mkdir()
    return folder


@pytest.fixture
def library(tmp_path):
    root = tmp_path / 'library'
    for song_url in ARTWORK:
        track = root / song_url
        track.parent.mkdir(parents=True, exist_ok=True)
        track.write_bytes(b'')
    return root


@pytest.fixture
def embedded_artwork(monkeypatch, library):
    """Serve distinct album art per audio file, without building real MP3 fixtures"""
    def _extract_album_art(self, mp3_file_path):
        song_url = Path(mp3_file_path).relative_to(library).as_posix()
        return ('jpg', ARTWORK[song_url])

    monkeypatch.setattr(CoverartCacheManager, '_extract_album_art', _extract_album_art)


def drain(manager):
    """Run the queued extractions that the worker thread would pick up"""
    while not manager.write_queue.empty():
        manager._save_to_cache(*manager.write_queue.get())


def test_same_filename_in_different_folders_gets_its_own_cover(cache_folder, library, embedded_artwork):
    manager = cache_manager(cache_folder)

    assert manager.get_cache_filename(library / BOOK_A, BOOK_A) == CACHE_PENDING
    assert manager.get_cache_filename(library / BOOK_B, BOOK_B) == CACHE_PENDING
    drain(manager)

    cover_a = manager.get_cache_filename(library / BOOK_A, BOOK_A)
    cover_b = manager.get_cache_filename(library / BOOK_B, BOOK_B)

    assert cover_a != cover_b
    assert (cache_folder / cover_a).read_bytes() == ARTWORK[BOOK_A]
    assert (cache_folder / cover_b).read_bytes() == ARTWORK[BOOK_B]


def test_the_same_song_keeps_hitting_the_same_cache_entry(cache_folder, library, embedded_artwork):
    manager = cache_manager(cache_folder)

    assert manager.get_cache_filename(library / BOOK_A, BOOK_A) == CACHE_PENDING
    drain(manager)

    cover = manager.get_cache_filename(library / BOOK_A, BOOK_A)

    assert cover != CACHE_PENDING
    assert manager.get_cache_filename(library / BOOK_A, BOOK_A) == cover
    assert manager.write_queue.empty()  # A cached cover must not be extracted again


def test_a_missing_cover_does_not_suppress_same_named_files_elsewhere(cache_folder, library, monkeypatch):
    monkeypatch.setattr(
        CoverartCacheManager,
        '_extract_album_art',
        lambda self, mp3_file_path: (NO_COVER_ART_EXTENSION, b''),
    )
    manager = cache_manager(cache_folder)

    manager.get_cache_filename(library / BOOK_A, BOOK_A)
    drain(manager)

    assert manager.get_cache_filename(library / BOOK_A, BOOK_A) == NO_CACHE
    assert manager.get_cache_filename(library / BOOK_B, BOOK_B) == CACHE_PENDING


def test_the_file_extension_is_part_of_the_cache_key():
    manager = CoverartCacheManager.__new__(CoverartCacheManager)

    mp3 = manager.generate_cache_key('Das Neinhorn/Kapitel 1.mp3')
    m4b = manager.generate_cache_key('Das Neinhorn/Kapitel 1.m4b')

    assert mp3 != m4b


def test_migration_purges_covers_written_with_an_older_cache_key(cache_folder):
    manager = cache_manager(cache_folder)
    stale = cache_folder / 'cover-beb9192b.jpg'
    stale.write_bytes(b'stale')
    gitkeep = cache_folder / '.gitkeep'
    gitkeep.touch()

    manager._migrate_cache()

    assert not stale.exists()
    assert gitkeep.exists()  # Docker bind-mounts the cache folder, .gitkeep is tracked
    assert (cache_folder / CACHE_SCHEMA_MARKER).read_text() == CACHE_SCHEMA_VERSION


def test_migration_leaves_an_up_to_date_cache_alone(cache_folder):
    manager = cache_manager(cache_folder)
    (cache_folder / CACHE_SCHEMA_MARKER).write_text(CACHE_SCHEMA_VERSION)
    cover = cache_folder / 'cover-0123abcd.jpg'
    cover.write_bytes(b'current')

    manager._migrate_cache()

    assert cover.exists()


def test_flushing_keeps_the_schema_marker(cache_folder):
    manager = cache_manager(cache_folder)
    marker = cache_folder / CACHE_SCHEMA_MARKER
    marker.write_text(CACHE_SCHEMA_VERSION)
    cover = cache_folder / 'cover-0123abcd.jpg'
    cover.write_bytes(b'current')

    manager.flush_cache()

    assert not cover.exists()
    assert marker.exists()  # Otherwise the next start would purge the cache all over again
