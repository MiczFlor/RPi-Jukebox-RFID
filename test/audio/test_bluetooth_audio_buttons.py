import sys
from types import SimpleNamespace
from unittest.mock import patch
from unittest.mock import MagicMock

import pytest

import jukebox.plugs as plugin

sys.modules.setdefault('jukebox.publishing', MagicMock())


def dummy_decorator(function):
    return function


plugin.register = dummy_decorator
plugin.initialize = dummy_decorator
plugin.atexit = dummy_decorator

sys.modules.setdefault('evdev', MagicMock())
from components.controls import bluetooth_audio_buttons  # noqa: E402


@patch.object(bluetooth_audio_buttons, 'activate')
def test_audio_monitor_activates_bluetooth_buttons(activate):
    bluetooth_audio_buttons.activate_from_audio_monitor('Headset', True)

    activate.assert_called_once_with('Headset', exact=False)


@patch.object(bluetooth_audio_buttons, 'activate')
def test_audio_monitor_ignores_non_bluetooth_buttons(activate):
    bluetooth_audio_buttons.activate_from_audio_monitor('USB Audio', False)

    activate.assert_not_called()


@pytest.mark.parametrize(
    ('driver', 'proplist'),
    [
        (
            'PipeWire',
            {'device.api': 'bluez5', 'device.description': 'PipeWire Headset'},
        ),
        (
            'module-bluez5-device.c',
            {'device.bus': 'bluetooth', 'device.description': 'PulseAudio Headset'},
        ),
    ],
)
def test_startup_discovers_bluetooth_cards(monkeypatch, driver, proplist):
    activate = MagicMock()
    callback_handler = MagicMock()
    audio_monitor = SimpleNamespace(on_connect_callbacks=callback_handler)
    volume_control = MagicMock()
    volume_control.card_list.return_value = [
        SimpleNamespace(driver=driver, proplist=proplist),
    ]

    monkeypatch.setattr(bluetooth_audio_buttons, 'activate', activate)
    monkeypatch.setattr(bluetooth_audio_buttons.cfg, 'setndefault',
                        MagicMock(return_value=True))
    monkeypatch.setattr(bluetooth_audio_buttons.cfg, 'getn',
                        MagicMock(return_value=None))
    monkeypatch.setattr(bluetooth_audio_buttons.jukebox.utils, 'bind_rpc_command',
                        MagicMock())
    monkeypatch.setattr(bluetooth_audio_buttons.components.volume,
                        'audio_monitor', audio_monitor, raising=False)
    monkeypatch.setattr(bluetooth_audio_buttons.components.volume,
                        'volume_control', volume_control, raising=False)

    bluetooth_audio_buttons.initialize()

    callback_handler.register.assert_called_once_with(
        bluetooth_audio_buttons.activate_from_audio_monitor)
    activate.assert_called_once_with(
        proplist['device.description'], exact=False, open_initial_delay=0.1)
