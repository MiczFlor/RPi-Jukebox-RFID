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
