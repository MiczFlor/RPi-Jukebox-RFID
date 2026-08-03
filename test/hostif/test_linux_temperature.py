import importlib
import logging
import sys
import threading
from unittest.mock import MagicMock

import pytest

import jukebox.plugs as plugin


def _passthrough_decorator(obj=None, **ignored_kwargs):
    if obj is None:
        return lambda decorated: decorated
    return obj


@pytest.fixture
def hostif_linux(monkeypatch):
    monkeypatch.setattr(plugin, 'register', _passthrough_decorator)
    monkeypatch.setattr(plugin, 'initialize', _passthrough_decorator)
    monkeypatch.setattr(plugin, 'finalize', _passthrough_decorator)
    monkeypatch.setattr(plugin, 'atexit', _passthrough_decorator)
    monkeypatch.setattr(plugin, 'loaded_as', lambda ignored_name: 'host')
    publishing_module = sys.modules.get('jukebox.publishing')
    if publishing_module is None:
        publishing_module = importlib.import_module('jukebox.publishing')
    monkeypatch.setattr(
        sys.modules['jukebox'],
        'publishing',
        publishing_module,
        raising=False,
    )

    sys.modules.pop('components.hostif.linux', None)
    module = importlib.import_module('components.hostif.linux')
    yield module
    sys.modules.pop('components.hostif.linux', None)


def _temperature_config(*keys, value):
    return {
        'enabled': True,
        'timer_interval_sec': 10,
    }.get(keys[-1], value)


def _patch_get_publisher(hostif_linux, monkeypatch, get_publisher):
    monkeypatch.setattr(
        hostif_linux.jukebox.publishing,
        'get_publisher',
        get_publisher,
    )
    timer_module = sys.modules[hostif_linux.GenericEndlessTimerClass.__module__]
    monkeypatch.setattr(timer_module.publishing, 'get_publisher', get_publisher)


def test_unavailable_sensor_leaves_temperature_timer_disabled(
        hostif_linux, monkeypatch, caplog):
    publisher = MagicMock()
    monkeypatch.setattr(hostif_linux.cfg, 'setndefault', _temperature_config)
    _patch_get_publisher(
        hostif_linux,
        monkeypatch,
        MagicMock(return_value=publisher),
    )
    monkeypatch.setattr(hostif_linux, 'get_cpu_temperature',
                        MagicMock(side_effect=FileNotFoundError('thermal sensor missing')))

    with caplog.at_level(logging.WARNING, logger='jb.host.lnx'):
        hostif_linux.finalize()

    assert hostif_linux.timer_temperature.timer_thread is None
    publisher.send.assert_called_once()
    timer_topic, timer_state = publisher.send.call_args.args
    assert timer_topic == 'host.timer.cputemp'
    assert timer_state['enabled'] is False
    publisher.revoke.assert_called_once_with('host.temperature.cpu')
    assert [record.levelno for record in caplog.records] == [logging.WARNING]
    assert 'CPU temperature sensor unavailable' in caplog.text


def test_initial_temperature_read_publishes_and_starts_timer(
        hostif_linux, monkeypatch):
    publisher = MagicMock()
    start = MagicMock()
    monkeypatch.setattr(hostif_linux.cfg, 'setndefault', _temperature_config)
    _patch_get_publisher(
        hostif_linux,
        monkeypatch,
        MagicMock(return_value=publisher),
    )
    monkeypatch.setattr(hostif_linux, 'get_cpu_temperature',
                        MagicMock(return_value=47.2))
    monkeypatch.setattr(hostif_linux.GenericEndlessTimerClass, 'start', start)

    hostif_linux.finalize()

    publisher.send.assert_any_call('host.temperature.cpu', '47.2')
    start.assert_called_once_with()


def test_later_read_failure_cancels_and_revokes_from_timer_thread(
        hostif_linux, monkeypatch):
    timer = MagicMock()
    publisher = MagicMock()
    publisher_threads = []

    def get_publisher():
        publisher_threads.append(threading.current_thread())
        return publisher

    monkeypatch.setattr(hostif_linux, 'timer_temperature', timer, raising=False)
    monkeypatch.setattr(hostif_linux, 'get_cpu_temperature',
                        MagicMock(side_effect=OSError('sensor read failed')))
    _patch_get_publisher(hostif_linux, monkeypatch, get_publisher)

    worker = threading.Thread(
        target=hostif_linux.publish_cpu_temperature,
        name='host.timer.cputemp',
    )
    worker.start()
    worker.join()

    timer.cancel.assert_called_once_with()
    publisher.revoke.assert_called_once_with('host.temperature.cpu')
    assert publisher_threads == [worker]
