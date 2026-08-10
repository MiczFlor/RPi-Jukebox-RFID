from contextlib import nullcontext
from types import SimpleNamespace
from unittest.mock import Mock, sentinel

import mpd
import pytest

import jukebox.publishing as publishing

from components.player.backends.mpd import PlayerMPD


def mpd_backend():
    return PlayerMPD.__new__(PlayerMPD)


@pytest.mark.parametrize(
    ('pos', 'expected_args'),
    [
        (None, ()),
        # Position 0 must reach mpd instead of being mistaken for an omitted argument
        (0, (0,)),
        (3, (3,)),
        # RPC arguments arrive from JSON and from YAML card configurations
        ('3', (3,)),
    ],
)
def test_play_starts_at_the_requested_playlist_position(pos, expected_args):
    backend = mpd_backend()
    backend.mpd_lock = nullcontext()
    play = Mock()
    backend.mpd_client = SimpleNamespace(play=play)

    backend.play(pos)

    play.assert_called_once_with(*expected_args)


def test_play_reports_a_position_outside_the_playlist():
    backend = mpd_backend()
    backend.mpd_lock = nullcontext()
    backend.mpd_client = SimpleNamespace(
        play=Mock(side_effect=mpd.base.CommandError('Bad song index')),
    )

    with pytest.raises(mpd.base.CommandError):
        backend.play(99)


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
