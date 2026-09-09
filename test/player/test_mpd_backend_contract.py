from contextlib import nullcontext
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock, sentinel

import components.player
import jukebox.publishing as publishing

from components.player.backends.mpd import PlayerMPD


def mpd_backend():
    return PlayerMPD.__new__(PlayerMPD)


def test_library_source_describes_local_views():
    source = mpd_backend().library_source()

    assert source == {
        'id': 'mpd',
        'label': 'Local',
        'views': [
            {
                'id': 'albums',
                'label': 'Albums',
                'kind': 'items',
                'content_types': ['album'],
            },
            {
                'id': 'folders',
                'label': 'Folders',
                'kind': 'folders',
                'content_types': [],
            },
        ],
    }


def test_album_catalog_adds_provider_metadata():
    backend = mpd_backend()
    backend.mpd_lock = nullcontext()
    backend.mpd_client = SimpleNamespace(list=sentinel.list)
    backend.mpd_retry_with_mutex = Mock(return_value=[
        {'albumartist': 'Reader', 'album': 'Stories'},
    ])

    assert backend.list_library_items(['album']) == [{
        'albumartist': 'Reader',
        'album': 'Stories',
        'provider': 'mpd',
        'content_uri': None,
        'cover_url': None,
        'content_type': 'album',
    }]
    assert backend.list_library_items(['playlist']) == []


def test_inactive_backend_does_not_publish_status(monkeypatch):
    publisher = Mock()
    monkeypatch.setattr(publishing, 'get_publisher', Mock(return_value=publisher))
    backend = mpd_backend()
    backend.mpd_status = {}
    backend.mpd_client = SimpleNamespace(
        status=sentinel.status,
        currentsong=sentinel.current_song,
    )
    backend.mpd_retry_with_mutex = Mock(side_effect=[
        {'state': 'stop'},
        {},
        {'state': 'stop'},
        {},
    ])
    backend.current_folder_status = {}
    backend.music_player_status = {'player_status': {}}
    backend._active = False

    backend._mpd_status_poll()

    publisher.send.assert_not_called()

    backend.set_active(True)
    publisher.reset_mock()
    backend._mpd_status_poll()

    publisher.send.assert_called_once_with(
        'playerstatus',
        {'state': 'stop', 'provider': 'mpd'},
    )


def test_get_single_coverart_keys_the_cache_on_the_library_relative_path(monkeypatch):
    monkeypatch.setattr(components.player, 'get_music_library_path', lambda: '/home/pi/audiofolders')
    backend = mpd_backend()
    backend.coverart_cache_manager = Mock()
    song_url = 'Das Neinhorn/1-01 Kapitel 1.mp3'

    backend.get_single_coverart(song_url)

    backend.coverart_cache_manager.get_cache_filename.assert_called_once_with(
        Path('/home/pi/audiofolders', song_url),
        song_url,
    )
