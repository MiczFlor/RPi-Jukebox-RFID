import logging
import threading
import time

import pytest

from jukebox.multitimer import (
    GenericEndlessTimerClass,
    GenericMultiTimerClass,
    GenericTimerClass,
)


class RecordingPublisher:
    def __init__(self):
        self.messages = []
        self.lock = threading.Lock()

    def send(self, topic, state):
        with self.lock:
            self.messages.append((
                threading.current_thread(),
                topic,
                state.copy(),
            ))


@pytest.fixture
def publisher(monkeypatch):
    publisher = RecordingPublisher()
    monkeypatch.setattr(
        'jukebox.multitimer.publishing.get_publisher',
        lambda: publisher,
    )
    return publisher


def wait_until(predicate, timeout=1):
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if predicate():
            return
        time.sleep(0.002)
    pytest.fail('condition was not met before timeout')


def test_one_shot_executes_and_clamps_remaining_time(publisher):
    called = threading.Event()
    timer = GenericTimerClass('test.once', 0.02, called.set)

    timer.start()
    assert timer.get_state()['enabled'] is True
    assert 0 <= timer.get_state()['remaining_seconds'] <= 0.02
    assert called.wait(1)
    wait_until(lambda: not timer.is_alive())

    assert timer.get_state()['remaining_seconds'] == 0
    timer.close()


def test_cancel_and_trigger(publisher):
    called = threading.Event()
    timer = GenericTimerClass('test.control', 10, called.set)

    timer.start()
    timer.cancel()
    assert not called.wait(0.03)
    assert timer.get_state()['enabled'] is False

    timer.start()
    timer.trigger()
    assert called.wait(1)
    wait_until(lambda: not timer.is_alive())
    timer.close()


def test_restart_is_atomic_and_restart_false_keeps_deadline(publisher):
    calls = []
    called = threading.Event()

    def callback():
        calls.append(time.monotonic())
        called.set()

    timer = GenericTimerClass('test.restart', 0.2, callback)
    timer.start()
    first_thread = timer.timer_thread
    first_deadline = timer._deadline

    timer.start(0.03, restart=False)
    assert timer.timer_thread is first_thread
    assert timer._deadline == first_deadline
    assert timer.get_timeout() == 0.2

    timer.start(0.04)
    assert timer.timer_thread is not first_thread
    assert called.wait(1)
    time.sleep(0.05)
    assert len(calls) == 1
    timer.close()


def test_set_timeout_replaces_running_generation(publisher):
    called = threading.Event()
    timer = GenericTimerClass('test.timeout', 1, called.set)
    timer.start()
    first_thread = timer.timer_thread

    assert timer.set_timeout(0.02) == 0.02
    assert timer.timer_thread is not first_thread
    assert timer.get_timeout() == 0.02
    assert called.wait(1)
    timer.close()


def test_restart_at_expiry_suppresses_stale_callback(publisher):
    calls = []
    called = threading.Event()
    timer = GenericTimerClass(
        'test.boundary',
        0.03,
        lambda: (calls.append(timer.timer_thread), called.set()),
    )

    timer.start()
    old_worker = timer.timer_thread
    time.sleep(0.02)
    timer.start(0.03)
    replacement = timer.timer_thread

    assert called.wait(1)
    time.sleep(0.04)
    assert calls == [replacement]
    assert old_worker is not replacement
    timer.close()


def test_periodic_timer_uses_fixed_delay_and_can_cancel_itself(publisher):
    timestamps = []
    timer = None
    finished = threading.Event()

    def callback():
        timestamps.append(time.monotonic())
        time.sleep(0.015)
        if len(timestamps) == 3:
            timer.cancel()
            finished.set()

    timer = GenericEndlessTimerClass('test.periodic', 0.015, callback)
    timer.start()

    assert finished.wait(1)
    wait_until(lambda: not timer.is_alive())
    assert len(timestamps) == 3
    assert all(
        later - earlier >= 0.025
        for earlier, later in zip(timestamps, timestamps[1:])
    )
    timer.close()


def test_callback_exception_stops_generation_and_publishes_once(
        publisher,
        caplog):
    def callback():
        raise RuntimeError('callback failed')

    timer = GenericEndlessTimerClass('test.failure', 0.01, callback)
    with caplog.at_level(logging.ERROR, logger='jb.multitimers'):
        timer.start()
        wait_until(lambda: not timer.is_alive())

    terminal = [
        message for message in publisher.messages
        if message[1] == 'test.failure' and message[2]['enabled'] is False
    ]
    # One initial disabled publication and one terminal transition.
    assert len(terminal) == 2
    assert terminal[-1][0] is timer.timer_thread
    assert caplog.text.count("Timer 'test.failure' callback failed") == 1
    timer.close()


def test_close_joins_workers_and_prevents_later_starts(publisher):
    timer = GenericEndlessTimerClass('test.close', 10, lambda: None)
    timer.start()
    worker = timer.timer_thread

    timer.close()

    assert not worker.is_alive()
    assert not timer.is_alive()
    timer.start(0)
    assert timer.timer_thread is worker
    assert not worker.is_alive()


def test_multi_timer_builds_one_callback_and_preserves_iteration_order(
        publisher):
    constructed = []
    iterations = []
    complete = threading.Event()

    class Callback:
        def __init__(self, prefix, *, iterations):
            constructed.append((prefix, iterations))

        def __call__(self, suffix, *, iteration):
            iterations.append((suffix, iteration))
            if iteration == 0:
                complete.set()

    timer = GenericMultiTimerClass(
        'test.multi',
        3,
        0.01,
        Callback,
        args=['builder'],
        kwargs={},
    )
    timer.args = ['callback']
    timer.start()

    assert complete.wait(1)
    wait_until(lambda: not timer.is_alive())
    assert constructed == [('builder', 3)]
    assert iterations == [
        ('callback', 2),
        ('callback', 1),
        ('callback', 0),
    ]
    timer.close()
