import sys
from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest

import jukebox.plugs as plugin

sys.modules.setdefault('jukebox.publishing', MagicMock())


def dummy_decorator(function):
    return function


plugin.initialize = dummy_decorator
plugin.finalize = dummy_decorator
plugin.atexit = dummy_decorator
plugin.tag = dummy_decorator

import components.volume as volume  # noqa: E402


@pytest.fixture
def monitor(monkeypatch):
    audio_monitor = volume.AudioMonitor.__new__(volume.AudioMonitor)
    audio_monitor._audio_server = MagicMock()
    audio_monitor._toggle_on_connect = False
    audio_monitor.last_event = [
        SimpleNamespace(facility='card', t='new', index=7),
    ]
    audio_monitor.on_connect_callbacks = MagicMock()
    monkeypatch.setattr(volume, 'volume_control', MagicMock(), raising=False)
    return audio_monitor


@pytest.mark.parametrize(
    ('driver', 'proplist', 'expected_name', 'is_bluetooth'),
    [
        (
            'PipeWire',
            {'device.api': 'bluez5', 'device.description': 'PipeWire Headset'},
            'PipeWire Headset',
            True,
        ),
        (
            'module-bluez5-device.c',
            {'device.bus': 'bluetooth', 'device.description': 'PulseAudio Headset'},
            'PulseAudio Headset',
            True,
        ),
        (
            'module-alsa-card.c',
            {'device.api': 'alsa', 'alsa.card_name': 'USB Audio'},
            'USB Audio',
            False,
        ),
    ],
)
def test_new_card_callback_uses_stable_bluetooth_properties(
        monitor, driver, proplist, expected_name, is_bluetooth):
    monitor._audio_server.card_list.return_value = [
        SimpleNamespace(index=7, driver=driver, proplist=proplist),
    ]

    monitor._handle_event()

    monitor.on_connect_callbacks._run_callbacks.assert_called_once_with(
        expected_name, is_bluetooth)


@pytest.mark.parametrize(
    ('proplist', 'should_switch'),
    [
        ({'device.api': 'bluez5', 'device.description': 'Headset'}, True),
        ({'device.api': 'alsa', 'alsa.card_name': 'USB Audio'}, False),
    ],
)
def test_toggle_on_connect_only_switches_for_bluetooth(
        monitor, proplist, should_switch):
    monitor._toggle_on_connect = True
    monitor._audio_server.card_list.return_value = [
        SimpleNamespace(index=7, driver='PipeWire', proplist=proplist),
    ]

    monitor._handle_event()

    if should_switch:
        volume.volume_control._set_output.assert_called_once_with(
            monitor._audio_server, 1)
    else:
        volume.volume_control._set_output.assert_not_called()


def test_unknown_card_index_does_not_run_callbacks(monitor):
    monitor._audio_server.card_list.return_value = [
        SimpleNamespace(index=3, driver='PipeWire', proplist={}),
    ]

    monitor._handle_event()

    monitor.on_connect_callbacks._run_callbacks.assert_not_called()
