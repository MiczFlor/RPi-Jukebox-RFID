import os

import pytest

from jukebox.library import LibraryError, MusicLibrary


@pytest.fixture
def music_library(tmp_path):
    root = tmp_path / 'music'
    root.mkdir()
    updates = []
    library = MusicLibrary(lambda: str(root), lambda: updates.append('update') or 'job-1')
    return library, root, updates


def test_upload_is_published_atomically_and_rejects_duplicates(music_library):
    library, root, _ = music_library
    album = root / 'Album'
    album.mkdir()

    upload = library.start_upload('Album', 'song.mp3')
    assert (album / 'song.mp3').read_bytes() == b''
    upload.write(b'audio data')
    upload.finish()

    assert (album / 'song.mp3').read_bytes() == b'audio data'
    assert not list(album.glob('.phoniebox-upload-*'))

    with pytest.raises(LibraryError) as error:
        library.start_upload('Album', 'song.mp3')
    assert error.value.status == 409
    assert error.value.code == 'duplicate_name'
    assert (album / 'song.mp3').read_bytes() == b'audio data'


def test_cancelled_upload_removes_temporary_and_reserved_files(music_library):
    library, root, _ = music_library

    upload = library.start_upload('.', 'cancelled.flac')
    upload.write(b'partial')
    upload.abort()

    assert not (root / 'cancelled.flac').exists()
    assert not list(root.glob('.phoniebox-upload-*'))


@pytest.mark.parametrize('name', [
    'track.MP3',
    'playlist.m3u8',
    'station.livestream.txt',
    'show.podcast.txt',
    'cover.webp',
])
def test_supported_library_file_types_are_accepted(music_library, name):
    library, root, _ = music_library

    upload = library.start_upload('.', name)
    upload.abort()

    assert not (root / name).exists()


@pytest.mark.parametrize('name', ['notes.txt', 'archive.zip', '.hidden.mp3', '../track.mp3'])
def test_unsupported_or_invalid_file_names_are_rejected(music_library, name):
    library, _, _ = music_library

    with pytest.raises(LibraryError) as error:
        library.start_upload('.', name)

    assert error.value.status in (400, 415)


def test_create_folder_and_delete_non_empty_folder(music_library):
    library, root, _ = music_library

    path = library.create_folder('.', 'New Album')
    (root / path / 'track.mp3').write_bytes(b'audio')
    nested = root / path / 'Disc 2'
    nested.mkdir()
    (nested / 'track.mp3').write_bytes(b'audio')

    assert path == 'New Album'
    assert library.delete_entries([path]) == [path]
    assert not (root / path).exists()


def test_list_entries_includes_manageable_files_and_skips_external_symlinks(music_library, tmp_path):
    library, root, _ = music_library
    (root / 'Album').mkdir()
    (root / 'track.mp3').touch()
    (root / 'cover.jpg').touch()
    (root / 'station.livestream.txt').touch()
    (root / 'notes.pdf').touch()
    (root / '.phoniebox-upload-part').touch()
    outside = tmp_path / 'outside'
    outside.mkdir()
    (root / 'external').symlink_to(outside, target_is_directory=True)

    assert library.list_entries('.') == [
        {'name': 'Album', 'relpath': 'Album', 'type': 'directory'},
        {'name': 'cover.jpg', 'relpath': 'cover.jpg', 'type': 'image'},
        {'name': 'notes.pdf', 'relpath': 'notes.pdf', 'type': 'other'},
        {
            'name': 'station.livestream.txt',
            'relpath': 'station.livestream.txt',
            'type': 'stream',
        },
        {'name': 'track.mp3', 'relpath': 'track.mp3', 'type': 'file'},
    ]


def test_delete_validates_all_paths_before_removing_anything(music_library):
    library, root, _ = music_library
    existing = root / 'keep.mp3'
    existing.write_bytes(b'audio')

    with pytest.raises(LibraryError) as error:
        library.delete_entries(['keep.mp3', '../outside.mp3'])

    assert error.value.code == 'invalid_path'
    assert existing.exists()


def test_root_and_symlink_escape_are_rejected(music_library, tmp_path):
    library, root, _ = music_library
    outside = tmp_path / 'outside'
    outside.mkdir()
    (outside / 'track.mp3').write_bytes(b'outside')
    (root / 'outside').symlink_to(outside, target_is_directory=True)

    with pytest.raises(LibraryError) as root_error:
        library.delete_entries(['.'])
    assert root_error.value.code == 'invalid_path'

    with pytest.raises(LibraryError) as upload_error:
        library.start_upload('outside', 'new.mp3')
    assert upload_error.value.code == 'invalid_path'

    with pytest.raises(LibraryError) as delete_error:
        library.delete_entries(['outside'])
    assert delete_error.value.code == 'invalid_path'
    assert (outside / 'track.mp3').exists()


def test_upload_does_not_replace_file_created_during_transfer(music_library):
    library, root, _ = music_library
    upload = library.start_upload('.', 'race.mp3')
    upload.write(b'upload')

    reserved = root / 'race.mp3'
    reserved.unlink()
    reserved.write_bytes(b'other writer')

    with pytest.raises(LibraryError) as error:
        upload.finish()

    assert error.value.code == 'duplicate_name'
    assert reserved.read_bytes() == b'other writer'
    assert not list(root.glob('.phoniebox-upload-*'))


def test_update_returns_mpd_job_identifier(music_library):
    library, _, updates = music_library

    assert library.update() == 'job-1'
    assert updates == ['update']


def test_uploaded_file_mode_is_shared_writable(music_library):
    library, root, _ = music_library
    upload = library.start_upload('.', 'track.wav')
    upload.write(b'audio')
    upload.finish()

    assert os.stat(root / 'track.wav').st_mode & 0o777 == 0o666
