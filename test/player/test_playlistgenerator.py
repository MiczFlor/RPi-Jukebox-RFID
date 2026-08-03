import pytest

from jukebox.library import LibraryError
from jukebox.playlistgenerator import PlaylistCollector


def test_pdf_is_excluded_from_folder_content_and_playlist(tmp_path):
    mp3 = tmp_path / 'track.mp3'
    mp3.touch()
    (tmp_path / 'booklet.pdf').touch()

    collector = PlaylistCollector(str(tmp_path))
    collector.parse()
    assert list(collector) == [str(mp3)]

    collector.get_directory_content()
    assert [entry['name'] for entry in collector.playlist] == ['track.mp3']


def test_folder_content_cannot_escape_music_library(tmp_path):
    music = tmp_path / 'music'
    music.mkdir()
    outside = tmp_path / 'outside'
    outside.mkdir()
    (outside / 'private.mp3').touch()
    collector = PlaylistCollector(str(music))

    with pytest.raises(LibraryError) as traversal_error:
        collector.get_directory_content('../outside')
    assert traversal_error.value.code == 'invalid_path'

    (music / 'linked').symlink_to(outside, target_is_directory=True)
    with pytest.raises(LibraryError) as symlink_error:
        collector.get_directory_content('linked')
    assert symlink_error.value.code == 'invalid_path'
