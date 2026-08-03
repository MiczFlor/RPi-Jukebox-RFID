import importlib.util
import logging
import threading
import time
from pathlib import Path

import pytest


PROJECT_ROOT = Path(__file__).parents[2]
MODULE_PATH = (
    PROJECT_ROOT
    / 'src/jukebox/components/timers/volume_fadeout_shutdown_timer.py'
)
SPEC = importlib.util.spec_from_file_location(
    'volume_fadeout_timer_under_test',
    MODULE_PATH,
)
fadeout_module = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(fadeout_module)

VolumeFadeoutAndShutdown = fadeout_module.VolumeFadeoutAndShutdown
VolumeFadeoutError = fadeout_module.VolumeFadeoutError


class FakeClock:
    def __init__(self):
        self.now = 0

    def __call__(self):
        return self.now

    def advance(self, seconds):
        self.now += seconds


class Publisher:
    def __init__(self):
        self.messages = []
        self.lock = threading.Lock()

    def send(self, topic, state):
        with self.lock:
            self.messages.append((topic, state.copy()))


def wait_until(predicate, timeout=1):
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if predicate():
            return
        time.sleep(0.002)
    pytest.fail('condition was not met before timeout')


def fire_scheduled_timer(timer):
    worker = timer.timer_thread
    assert worker is not None
    timer._timer.trigger()
    wait_until(
        lambda: timer.timer_thread is not worker or not worker.is_alive(),
    )


@pytest.fixture
def fadeout_factory(monkeypatch):
    timers = []
    publisher = Publisher()
    config_calls = []
    monkeypatch.setattr(
        fadeout_module.publishing,
        'get_publisher',
        lambda: publisher,
    )

    def set_default(*keys, value):
        config_calls.append((keys, value))
        return value

    monkeypatch.setattr(fadeout_module.cfg, 'setndefault', set_default)

    def create(
            *,
            clock=None,
            get_volume=lambda: 110,
            set_volume=lambda volume: None,
            shutdown_action=lambda: None):
        timer = VolumeFadeoutAndShutdown(
            'timers.timer_fade_volume',
            clock=clock or FakeClock(),
            get_volume=get_volume,
            set_volume=set_volume,
            shutdown_action=shutdown_action,
        )
        timers.append(timer)
        return timer

    yield create, publisher, config_calls

    for timer in timers:
        timer.close()


def test_minimum_validation_and_exact_duration_starts_fade_immediately(
        fadeout_factory):
    create, _, _ = fadeout_factory
    reads = []
    timer = create(get_volume=lambda: (reads.append(True), 110)[1])

    with pytest.raises(VolumeFadeoutError):
        timer.start(119)

    timer.start(120)

    assert reads == [True]
    assert timer.get_state()['fadeout_started'] is True
    assert timer.get_state()['remaining_seconds'] == 120
    assert timer.timer_thread is not None


def test_restart_false_and_restart_replace_pending_generation(
        fadeout_factory):
    create, _, _ = fadeout_factory
    clock = FakeClock()
    reads = []
    timer = create(
        clock=clock,
        get_volume=lambda: (reads.append(True), 110)[1],
    )
    timer.start(180)
    first_worker = timer.timer_thread

    timer.start(240, restart=False)
    assert timer.timer_thread is first_worker
    assert timer.get_state()['total_duration'] == 180

    timer.start(240)
    replacement = timer.timer_thread
    first_worker.trigger()
    wait_until(lambda: not first_worker.is_alive())

    assert replacement is not first_worker
    assert reads == []
    assert timer.get_state()['total_duration'] == 240


def test_cancellation_before_and_during_fade_suppresses_future_steps(
        fadeout_factory):
    create, _, _ = fadeout_factory
    clock = FakeClock()
    writes = []
    shutdowns = []
    before = create(
        clock=clock,
        set_volume=writes.append,
        shutdown_action=lambda: shutdowns.append(True),
    )
    before.start(180)
    worker = before.timer_thread
    before.cancel()
    worker.trigger()
    wait_until(lambda: not worker.is_alive())
    assert writes == []

    during = create(
        clock=clock,
        set_volume=writes.append,
        shutdown_action=lambda: shutdowns.append(True),
    )
    during.start(120)
    clock.advance(10)
    fire_scheduled_timer(during)
    during.cancel()
    time.sleep(0.02)

    assert writes == [110]
    assert shutdowns == []
    assert during.get_state()['enabled'] is False


def test_restart_during_fade_suppresses_stale_step(fadeout_factory):
    create, _, _ = fadeout_factory
    clock = FakeClock()
    writes = []
    timer = create(clock=clock, set_volume=writes.append)
    timer.start(120)
    stale_worker = timer.timer_thread

    timer.start(120)
    replacement = timer.timer_thread
    stale_worker.trigger()
    wait_until(lambda: not stale_worker.is_alive())

    assert replacement is not stale_worker
    assert writes == []
    clock.advance(10)
    fire_scheduled_timer(timer)
    assert writes == [110]


def test_twelve_ordered_steps_reach_zero_before_one_shutdown(
        fadeout_factory):
    create, _, _ = fadeout_factory
    clock = FakeClock()
    events = []
    timer = create(
        clock=clock,
        set_volume=lambda volume: events.append(('volume', volume)),
        shutdown_action=lambda: events.append(('shutdown', None)),
    )
    timer.start(120)

    for _ in range(12):
        clock.advance(10)
        fire_scheduled_timer(timer)

    assert events == [
        ('volume', 110),
        ('volume', 100),
        ('volume', 90),
        ('volume', 80),
        ('volume', 70),
        ('volume', 60),
        ('volume', 50),
        ('volume', 40),
        ('volume', 30),
        ('volume', 20),
        ('volume', 10),
        ('volume', 0),
        ('shutdown', None),
    ]
    assert timer.get_state()['enabled'] is False


def test_volume_read_failure_skips_fade_but_keeps_shutdown(
        fadeout_factory,
        caplog):
    create, _, _ = fadeout_factory
    clock = FakeClock()
    shutdowns = []

    def fail_read():
        raise OSError('mixer unavailable')

    timer = create(
        clock=clock,
        get_volume=fail_read,
        shutdown_action=lambda: shutdowns.append(True),
    )
    with caplog.at_level(
            logging.ERROR,
            logger='jb.timers.volume_fadeout'):
        timer.start(120)

    assert timer.get_state()['error'] == 'OSError: mixer unavailable'
    clock.advance(120)
    fire_scheduled_timer(timer)
    assert shutdowns == [True]
    assert 'fadeout will be skipped' in caplog.text


def test_volume_write_failures_are_published_and_later_steps_continue(
        fadeout_factory):
    create, publisher, _ = fadeout_factory
    clock = FakeClock()
    attempts = []
    shutdowns = []

    def write(volume):
        attempts.append(volume)
        if volume == 100:
            raise OSError('write failed')

    timer = create(
        clock=clock,
        set_volume=write,
        shutdown_action=lambda: shutdowns.append(True),
    )
    timer.start(120)
    for _ in range(12):
        clock.advance(10)
        fire_scheduled_timer(timer)

    assert attempts[-1] == 0
    assert len(attempts) == 12
    assert shutdowns == [True]
    assert any(
        state['error'] == 'OSError: write failed'
        for _, state in publisher.messages
        if state['enabled']
    )


def test_state_progress_remaining_and_publication(fadeout_factory):
    create, publisher, config_calls = fadeout_factory
    clock = FakeClock()
    timer = create(clock=clock)
    timer.start(180)
    clock.advance(45)

    state = timer.get_state()
    assert state['type'] == 'VolumeFadoutAndShutdown'
    assert state['remaining_seconds'] == 135
    assert state['progress_percent'] == 25
    assert state['error'] is None
    assert config_calls == [
        (('timers', 'volume_fadeout', 'default_timeout_sec'), 600),
    ]
    assert all(
        topic == 'timers.timer_fade_volume'
        for topic, _ in publisher.messages
    )


def test_compatibility_alias_and_obsolete_defaults_are_removed():
    assert (
        fadeout_module.VolumeFadoutAndShutdown
        is fadeout_module.VolumeFadeoutAndShutdown
    )
    config = (
        PROJECT_ROOT / 'resources/default-settings/jukebox.default.yaml'
    ).read_text()
    assert 'volume_fade_out:' not in config
    assert 'timer_fade_volume:' not in config
    assert 'volume_fadeout:' in config


def test_generic_multi_timer_has_no_remaining_consumers():
    source_root = PROJECT_ROOT / 'src'
    references = []
    for path in source_root.rglob('*.py'):
        if 'GenericMultiTimerClass' in path.read_text():
            references.append(path)
    assert references == []
