import importlib
import sys
import threading
from unittest.mock import MagicMock

import jukebox.plugs as plugin


def _passthrough_decorator(obj=None, **ignored_kwargs):
    if obj is None:
        return lambda decorated: decorated
    return obj


def test_timer_plugin_shutdown_closes_workers_without_writing_config(
        monkeypatch):
    monkeypatch.setattr(plugin, 'register', _passthrough_decorator)
    monkeypatch.setattr(plugin, 'finalize', _passthrough_decorator)
    monkeypatch.setattr(plugin, 'atexit', _passthrough_decorator)
    monkeypatch.setattr(plugin, 'loaded_as', lambda ignored_name: 'timers')
    monkeypatch.setattr(
        plugin,
        'call',
        lambda *args, **kwargs: {'state': 'stop'},
    )
    monkeypatch.setattr(plugin, 'call_ignore_errors', MagicMock())
    publisher = MagicMock()
    monkeypatch.setattr(
        'jukebox.multitimer.publishing.get_publisher',
        lambda: publisher,
    )

    sys.modules.pop('components.timers', None)
    timers = importlib.import_module('components.timers')
    monkeypatch.setattr(
        timers.cfg,
        'setndefault',
        lambda *keys, value: 0 if keys[-1] == 'timeout_sec' else value,
    )
    config_write = MagicMock()
    monkeypatch.setattr(timers.cfg, 'setn', config_write)

    timers.finalize()
    timers.timer_shutdown.start(30)
    timers.timer_stop_player.start(30)
    workers = [
        timers.timer_shutdown.timer_thread,
        timers.timer_stop_player.timer_thread,
    ]

    assert timers.atexit() == []

    config_write.assert_not_called()
    assert all(not worker.is_alive() for worker in workers)
    assert not any(
        thread.name.startswith('timers.')
        for thread in threading.enumerate()
    )
    sys.modules.pop('components.timers', None)
