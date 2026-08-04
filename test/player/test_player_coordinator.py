import logging
from types import SimpleNamespace
from unittest.mock import Mock, call, sentinel

import pytest

from components.player.coordinator import PlayerCoordinator
from components.player.playcontentcallback import PlayCardState, PlayContentCallbacks
from components.rpc_command_alias import cmd_alias_definitions


def backend_with(**methods):
    defaults = {
        'stop': Mock(),
        'exit': Mock(),
    }
    defaults.update(methods)
    return SimpleNamespace(**defaults)


def test_registers_and_selects_first_backend():
    coordinator = PlayerCoordinator()
    mpd_backend = backend_with()
    other_backend = backend_with()

    coordinator.register_backend('mpd', mpd_backend)
    coordinator.register_backend('other', other_backend)

    assert coordinator.list_backends() == ['mpd', 'other']
    assert coordinator.get_active_backend() == 'mpd'
    mpd_backend.stop.assert_not_called()


def test_rejects_invalid_backend_registrations():
    coordinator = PlayerCoordinator()
    coordinator.register_backend('mpd', backend_with())

    with pytest.raises(ValueError, match="must not be empty"):
        coordinator.register_backend('', backend_with())
    with pytest.raises(ValueError, match="already registered"):
        coordinator.register_backend('mpd', backend_with())


@pytest.mark.parametrize(
    ('coordinator_method', 'call_args', 'backend_args'),
    [
        ('get_player_type_and_version', (), ()),
        ('update', (), ()),
        ('update_wait', (), ()),
        ('play', (), ()),
        ('stop', (), ()),
        ('pause', (), (1,)),
        ('pause', (0,), (0,)),
        ('prev', (), ()),
        ('next', (), ()),
        ('seek', (23,), (23,)),
        ('rewind', (), ()),
        ('replay', (), ()),
        ('toggle', (), ()),
        ('replay_if_stopped', (), ()),
        ('shuffle', (), ('toggle',)),
        ('shuffle', ('enable',), ('enable',)),
        ('repeat', (), ('toggle',)),
        ('repeat', ('disable',), ('disable',)),
        ('get_current_song', ('title',), ('title',)),
        ('map_filename_to_playlist_pos', ('song.mp3',), ('song.mp3',)),
        ('remove', (), ()),
        ('move', (), ()),
        ('play_single', ('album/song.mp3',), ('album/song.mp3',)),
        ('resume', (), ()),
        ('get_single_coverart', ('album/song.mp3',), ('album/song.mp3',)),
        ('get_album_coverart', ('Artist', 'Album'), ('Artist', 'Album')),
        ('flush_coverart_cache', (), ()),
        ('get_folder_content', ('album',), ('album',)),
        ('play_folder', ('album',), ('album', False)),
        ('play_folder', ('album', True), ('album', True)),
        ('play_album', ('Artist', 'Album'), ('Artist', 'Album')),
        ('queue_load', ('album',), ('album',)),
        ('playerstatus', (), ()),
        ('playlistinfo', (), ()),
        ('list_all_dirs', (), ()),
        ('list_albums', (), ()),
        ('list_songs_by_artist_and_album', ('Artist', 'Album'), ('Artist', 'Album')),
        ('get_song_by_url', ('album/song.mp3',), ('album/song.mp3',)),
        ('get_volume', (), ()),
        ('set_volume', (42,), (42,)),
    ],
)
def test_delegates_existing_player_contract(
        coordinator_method, call_args, backend_args):
    backend_method = Mock(return_value=sentinel.result)
    backend = backend_with(**{coordinator_method: backend_method})
    coordinator = PlayerCoordinator()
    coordinator.register_backend('mpd', backend)

    result = getattr(coordinator, coordinator_method)(*call_args)

    assert result is sentinel.result
    backend_method.assert_called_once_with(*backend_args)


def test_switch_stops_old_backend_before_new_content_starts():
    events = []
    mpd_backend = backend_with(stop=Mock(side_effect=lambda: events.append('mpd.stop')))
    streaming_backend = backend_with(
        play_single=Mock(side_effect=lambda content: events.append(f'play:{content}'))
    )
    coordinator = PlayerCoordinator()
    coordinator.register_backend('mpd', mpd_backend)
    coordinator.register_backend('streaming', streaming_backend)

    coordinator.select_backend('streaming')
    coordinator.play_single('service:track:123')

    assert events == ['mpd.stop', 'play:service:track:123']
    assert coordinator.get_active_backend() == 'streaming'


def test_selecting_active_backend_does_not_stop_it():
    backend = backend_with()
    coordinator = PlayerCoordinator()
    coordinator.register_backend('mpd', backend)

    assert coordinator.select_backend('mpd') == 'mpd'

    backend.stop.assert_not_called()


def test_unknown_backend_and_unsupported_operation_errors_are_clear():
    coordinator = PlayerCoordinator()
    coordinator.register_backend('mpd', backend_with())

    with pytest.raises(KeyError, match="Unknown player backend 'missing'"):
        coordinator.select_backend('missing')
    with pytest.raises(NotImplementedError, match="does not support 'play'"):
        coordinator.play()


def test_plain_folder_content_routes_to_mpd_backend():
    play_folder = Mock(return_value=sentinel.playback)
    coordinator = PlayerCoordinator()
    coordinator.register_backend('mpd', backend_with(play_folder=play_folder))

    result = coordinator.play_folder('stories/chapter-one')

    assert result is sentinel.playback
    play_folder.assert_called_once_with('stories/chapter-one', False)


@pytest.mark.parametrize(
    ('is_second_swipe', 'expected_state', 'expected_action'),
    [
        (False, PlayCardState.firstSwipe, 'play_folder'),
        (True, PlayCardState.secondSwipe, 'second_swipe'),
    ],
)
def test_play_card_callbacks_run_before_backend_action(
        is_second_swipe, expected_state, expected_action):
    events = []
    callbacks = PlayContentCallbacks('test_callbacks', logging.getLogger(__name__))
    callbacks.register(
        lambda content, state: events.append(call('callback', content, state))
    )
    backend = backend_with(
        is_second_swipe=Mock(return_value=is_second_swipe),
        play_folder=Mock(
            side_effect=lambda content, recursive: events.append(call('play_folder'))
        ),
        play_second_swipe=Mock(
            side_effect=lambda: events.append(call('second_swipe'))
        ),
    )
    coordinator = PlayerCoordinator(callbacks)
    coordinator.register_backend('mpd', backend)

    coordinator.play_card('stories', recursive=True)

    assert events == [
        call('callback', 'stories', expected_state),
        call(expected_action),
    ]
    backend.is_second_swipe.assert_called_once_with('stories')
    if is_second_swipe:
        backend.play_folder.assert_not_called()
        backend.play_second_swipe.assert_called_once_with()
    else:
        backend.play_folder.assert_called_once_with('stories', True)
        backend.play_second_swipe.assert_not_called()


def test_playerstatus_is_returned_without_translation():
    player_status = {
        'state': 'play',
        'songid': '4',
        'title': 'Story',
        'artist': 'Reader',
        'album': 'Collection',
        'file': 'stories/story.mp3',
        'elapsed': '12.5',
        'duration': '60.0',
        'random': '0',
        'repeat': '0',
        'single': '0',
    }
    coordinator = PlayerCoordinator()
    coordinator.register_backend(
        'mpd', backend_with(playerstatus=Mock(return_value=player_status))
    )

    assert coordinator.playerstatus() is player_status


def test_existing_rpc_aliases_still_target_player_ctrl():
    expected_methods = {
        'play_card': 'play_card',
        'play_album': 'play_album',
        'play_single': 'play_single',
        'play_folder': 'play_folder',
        'play': 'play',
        'pause': 'pause',
        'next_song': 'next',
        'prev_song': 'prev',
        'toggle': 'toggle',
        'shuffle': 'shuffle',
        'repeat': 'repeat',
        'flush_coverart_cache': 'flush_coverart_cache',
    }

    for alias, method in expected_methods.items():
        definition = cmd_alias_definitions[alias]
        assert definition['package'] == 'player'
        assert definition['plugin'] == 'ctrl'
        assert definition['method'] == method


def test_exit_closes_all_backends_in_reverse_registration_order():
    first = backend_with(exit=Mock(return_value=sentinel.first))
    second = backend_with(exit=Mock(return_value=sentinel.second))
    coordinator = PlayerCoordinator()
    coordinator.register_backend('first', first)
    coordinator.register_backend('second', second)

    assert coordinator.exit() == [sentinel.second, sentinel.first]
