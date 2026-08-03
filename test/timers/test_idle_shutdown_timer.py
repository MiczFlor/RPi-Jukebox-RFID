import importlib.util
import logging
import os
import threading
import time
from pathlib import Path

import pytest


MODULE_PATH = (
    Path(__file__).parents[2]
    / 'src/jukebox/components/timers/idle_shutdown_timer.py'
)
SPEC = importlib.util.spec_from_file_location(
    'idle_shutdown_timer_under_test',
    MODULE_PATH,
)
idle_shutdown = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(idle_shutdown)

FilesystemSnapshotError = idle_shutdown.FilesystemSnapshotError
IdleShutdownTimer = idle_shutdown.IdleShutdownTimer
filesystem_fingerprint = idle_shutdown.filesystem_fingerprint


class FakeClock:
    def __init__(self):
        self.now = 0

    def __call__(self):
        return self.now

    def advance(self, seconds):
        self.now += seconds


class SnapshotSequence:
    def __init__(self, *values):
        self.values = list(values)
        self.calls = 0

    def __call__(self):
        value = self.values[min(self.calls, len(self.values) - 1)]
        self.calls += 1
        if isinstance(value, Exception):
            raise value
        return value


class Publisher:
    def __init__(self):
        self.messages = []

    def send(self, topic, state):
        self.messages.append((topic, state.copy()))


@pytest.fixture
def controller_factory(monkeypatch):
    controllers = []
    config_writes = []
    publisher = Publisher()
    monkeypatch.setattr(
        idle_shutdown.publishing,
        'get_publisher',
        lambda: publisher,
    )
    monkeypatch.setattr(
        idle_shutdown.cfg,
        'setn',
        lambda *keys, value: config_writes.append((keys, value)),
    )

    def create(
            *,
            idle_timeout=0,
            clock=None,
            playback_detector=lambda: False,
            ssh_detector=lambda: False,
            snapshotter=lambda: ('baseline',),
            shutdown_action=lambda: None):
        timer = IdleShutdownTimer(
            'timers',
            idle_timeout,
            clock=clock or FakeClock(),
            playback_detector=playback_detector,
            ssh_detector=ssh_detector,
            snapshotter=snapshotter,
            check_interval=3600,
            grace_seconds=60,
            shutdown_action=shutdown_action,
        )
        controllers.append(timer)
        return timer

    yield create, config_writes, publisher

    for timer in controllers:
        timer.close()


def wait_until(predicate, timeout=1):
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if predicate():
            return
        time.sleep(0.002)
    pytest.fail('condition was not met before timeout')


def test_disabled_and_invalid_startup_create_no_monitor_thread(
        controller_factory,
        caplog):
    create, _, _ = controller_factory
    disabled = create(idle_timeout=0)

    with caplog.at_level(
            logging.WARNING,
            logger='jb.timers.idle_shutdown_timer'):
        invalid = create(idle_timeout='not-a-timeout')

    assert disabled.timer_thread is None
    assert invalid.timer_thread is None
    assert disabled.get_state() == {
        'enabled': False,
        'running': False,
        'remaining_seconds': 0,
        'wait_seconds': 0,
    }
    assert 'remains disabled' in caplog.text


def test_enable_restart_and_restart_false(controller_factory):
    create, config_writes, _ = controller_factory
    clock = FakeClock()
    snapshots = SnapshotSequence(('a',), ('b',))
    timer = create(clock=clock, snapshotter=snapshots)

    timer.start(60)
    first_worker = timer.timer_thread
    first_deadline = timer._deadline
    clock.advance(5)
    timer.start(120, restart=False)

    assert timer.timer_thread is first_worker
    assert timer._deadline == first_deadline
    assert timer.get_state()['wait_seconds'] == 60
    assert config_writes == [
        (('timers', 'idle_shutdown', 'timeout_sec'), 60),
    ]

    timer.start(120)
    second_worker = timer.timer_thread
    wait_until(lambda: not first_worker.is_alive())

    assert second_worker is not first_worker
    assert timer.get_state()['remaining_seconds'] == 120
    assert timer.get_state()['wait_seconds'] == 120
    assert snapshots.calls == 2


def test_invalid_rpc_value_does_not_change_state_or_config(
        controller_factory):
    create, config_writes, _ = controller_factory
    timer = create()
    timer.start(60)
    state = timer.get_state()
    writes = list(config_writes)

    with pytest.raises(ValueError):
        timer.start(59)
    with pytest.raises(ValueError):
        timer.start('invalid')

    assert timer.get_state() == state
    assert config_writes == writes


def test_playback_ssh_and_file_activity_reset_deadline(
        controller_factory):
    create, _, _ = controller_factory
    clock = FakeClock()
    activity = {'playback': False, 'ssh': False}
    snapshots = SnapshotSequence(('a',), ('b',), ('c',))
    timer = create(
        clock=clock,
        playback_detector=lambda: activity['playback'],
        ssh_detector=lambda: activity['ssh'],
        snapshotter=snapshots,
    )
    timer.start(60)

    clock.advance(10)
    activity['playback'] = True
    timer._poll()
    assert timer.get_state()['running'] is False

    clock.advance(10)
    activity['playback'] = False
    timer._poll()
    assert timer.get_state()['running'] is True
    assert timer._deadline == 80

    clock.advance(10)
    activity['ssh'] = True
    timer._poll()
    assert timer.get_state()['running'] is False

    clock.advance(10)
    activity['ssh'] = False
    timer._poll()
    assert timer._deadline == 100

    clock.advance(60)
    timer._poll()
    assert timer._deadline == 160
    assert timer.get_state()['running'] is True
    # Start, playback end, SSH end, and idle expiry each establish/verify state.
    assert snapshots.calls == 4


def test_filesystem_scans_only_at_baseline_expiry_and_grace(
        controller_factory):
    create, _, _ = controller_factory
    clock = FakeClock()
    snapshots = SnapshotSequence(('same',))
    shutdowns = []
    timer = create(
        clock=clock,
        snapshotter=snapshots,
        shutdown_action=lambda: shutdowns.append(True),
    )
    timer.start(60)

    for _ in range(5):
        clock.advance(10)
        timer._poll()
    assert snapshots.calls == 1

    clock.advance(10)
    timer._poll()
    assert snapshots.calls == 2
    assert timer.get_state()['remaining_seconds'] == 60

    for _ in range(5):
        clock.advance(10)
        timer._poll()
    assert snapshots.calls == 2

    clock.advance(10)
    timer._poll()
    assert snapshots.calls == 3
    assert shutdowns == [True]


def test_filesystem_race_postpones_shutdown_and_recovers(
        controller_factory,
        caplog):
    create, _, _ = controller_factory
    clock = FakeClock()
    snapshots = SnapshotSequence(
        ('a',),
        FilesystemSnapshotError('entry disappeared'),
        ('b',),
    )
    shutdowns = []
    timer = create(
        clock=clock,
        snapshotter=snapshots,
        shutdown_action=lambda: shutdowns.append(True),
    )
    timer.start(60)

    clock.advance(60)
    with caplog.at_level(
            logging.WARNING,
            logger='jb.timers.idle_shutdown_timer'):
        timer._poll()
        timer._poll()

    assert snapshots.calls == 3
    assert shutdowns == []
    assert timer.get_state()['running'] is True
    assert timer._deadline == 120
    assert caplog.text.count('Filesystem activity check failed') == 1


def test_detector_error_logs_once_and_postpones_until_recovery(
        controller_factory,
        caplog):
    create, _, _ = controller_factory
    clock = FakeClock()
    detector = {'error': True}
    snapshots = SnapshotSequence(('a',), ('b',))

    def playback():
        if detector['error']:
            raise OSError('player unavailable')
        return False

    timer = create(
        clock=clock,
        playback_detector=playback,
        snapshotter=snapshots,
    )
    timer.start(60)

    clock.advance(60)
    with caplog.at_level(
            logging.WARNING,
            logger='jb.timers.idle_shutdown_timer'):
        timer._poll()
        timer._poll()
        detector['error'] = False
        timer._poll()

    assert caplog.text.count('Idle activity detector failed') == 1
    assert snapshots.calls == 2
    assert timer.get_state()['running'] is True
    assert timer._deadline == 120


def test_shutdown_is_latched_and_published_once(controller_factory):
    create, _, publisher = controller_factory
    clock = FakeClock()
    snapshots = SnapshotSequence(('same',))
    shutdowns = []
    timer = create(
        clock=clock,
        snapshotter=snapshots,
        shutdown_action=lambda: shutdowns.append(True),
    )
    timer.start(60)
    clock.advance(60)
    timer._poll()
    clock.advance(60)
    timer._poll()
    timer._poll()

    disabled = [
        state for topic, state in publisher.messages
        if topic == 'timers.timer_idle_shutdown'
        and state['enabled'] is False
    ]
    # Initial disabled state and one terminal transition.
    assert len(disabled) == 2
    assert shutdowns == [True]
    assert timer.get_state()['enabled'] is False


def test_cancel_persists_zero_while_close_preserves_configuration(
        controller_factory):
    create, config_writes, _ = controller_factory
    cancelled = create()
    cancelled.start(60)
    cancelled.cancel()

    assert config_writes[-1] == (
        ('timers', 'idle_shutdown', 'timeout_sec'),
        0,
    )
    assert cancelled.get_state()['enabled'] is False

    preserved = create()
    preserved.start(120)
    writes_before_close = list(config_writes)
    worker = preserved.timer_thread
    preserved.close()

    assert config_writes == writes_before_close
    assert not worker.is_alive()


def test_publication_uses_rpc_compatible_state(controller_factory):
    create, _, publisher = controller_factory
    timer = create()
    timer.start(60)

    topic, state = publisher.messages[-1]
    assert topic == 'timers.timer_idle_shutdown'
    assert set(state) == {
        'enabled',
        'running',
        'remaining_seconds',
        'wait_seconds',
    }
    assert state['enabled'] is True
    assert state['running'] is True


def test_restart_at_poll_boundary_has_no_lock_inversion(
        controller_factory):
    create, _, _ = controller_factory
    detector_entered = threading.Event()
    release_detector = threading.Event()
    block_detector = {'value': False}

    def playback():
        if block_detector['value']:
            detector_entered.set()
            assert release_detector.wait(1)
        return False

    timer = create(playback_detector=playback)
    timer.start(60)
    block_detector['value'] = True
    timer._monitor.trigger()
    assert detector_entered.wait(1)

    restart = threading.Thread(target=timer.start, args=(120,))
    restart.start()
    time.sleep(0.02)
    release_detector.set()
    restart.join(1)

    assert not restart.is_alive()
    assert timer.get_state()['wait_seconds'] == 120


def test_filesystem_fingerprint_detects_metadata_and_missing_roots(tmp_path):
    present = tmp_path / 'present'
    present.mkdir()
    track = present / 'track.mp3'
    track.write_bytes(b'a')
    missing = tmp_path / 'missing'

    first = filesystem_fingerprint([present, missing])
    track.write_bytes(b'longer')
    os.utime(track, ns=(track.stat().st_atime_ns, track.stat().st_mtime_ns + 1))
    second = filesystem_fingerprint([present, missing])

    assert first != second
    assert any(entry[1] == 'missing' for entry in first)
    assert all(len(entry) == 4 for entry in first)
