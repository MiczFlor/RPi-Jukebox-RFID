"""Threaded one-shot and fixed-delay periodic timers."""

import logging
import threading
from time import monotonic
from typing import Any, Callable, Dict, Optional

import jukebox.plugs as plugin
import jukebox.publishing as publishing


logger = logging.getLogger('jb.multitimers')


class MultiTimer(threading.Thread):
    """Execute a callback after each fixed-delay interval.

    Limited timers count iterations down from ``iterations - 1`` to zero.
    Negative iteration counts repeat until cancellation.
    """

    def __init__(
            self,
            interval: float,
            iterations: int,
            function: Callable,
            args=None,
            kwargs=None,
            *,
            owner=None,
            generation: Optional[int] = None,
            first_deadline: Optional[float] = None):
        super().__init__()
        self.interval = interval
        self.iterations = iterations
        self.function = function
        self.args = args if args is not None else []
        self.kwargs = kwargs if kwargs is not None else {}
        self.event = threading.Event()
        self.cancel_event = threading.Event()
        self.publish_callback = None
        self._cmd_cancel = False
        self._owner = owner
        self._generation = generation
        self._first_deadline = first_deadline

    def cancel(self):
        """Stop the timer and wake its worker."""
        logger.debug("Cancel timer '%s'", self.name)
        self._cmd_cancel = True
        self.cancel_event.set()
        self.event.set()

    def trigger(self):
        """Trigger the next callback immediately."""
        self.event.set()

    def _wait(self, deadline: float) -> bool:
        self.event.wait(max(0, deadline - monotonic()))
        self.event.clear()
        return not self.cancel_event.is_set()

    def _invoke(self, iteration: int) -> bool:
        if self._owner is not None:
            return self._owner._invoke(self, self._generation, iteration)
        self.function(*self.args, iteration=iteration, **self.kwargs)
        return True

    def _iteration_completed(self) -> bool:
        if self._owner is None:
            return not self.cancel_event.is_set()
        return self._owner._iteration_completed(self, self._generation)

    def _run_endless(self, deadline: float) -> None:
        logger.debug("Start timer '%s' in endless mode", self.name)
        while self._wait(deadline):
            if not self._invoke(-1) or not self._iteration_completed():
                break
            deadline = monotonic() + self.interval

    def _run_limited(self, deadline: float) -> bool:
        logger.debug(
            "Start timer '%s' with %s iterations",
            self.name,
            self.iterations,
        )
        if self.iterations == 0:
            return True
        for iteration in range(self.iterations - 1, -1, -1):
            if not self._wait(deadline):
                break
            if not self._invoke(iteration) or not self._iteration_completed():
                break
            if iteration == 0:
                return True
            deadline = monotonic() + self.interval
        return False

    def run(self):
        """Run until all iterations complete, cancellation, or callback failure."""
        standalone = self._owner is None
        if standalone and self.publish_callback is not None:
            self.publish_callback()

        completed = False
        deadline = self._first_deadline
        if deadline is None:
            deadline = monotonic() + self.interval

        try:
            if self.iterations < 0:
                self._run_endless(deadline)
            else:
                completed = self._run_limited(deadline)
        except Exception:
            logger.exception("Timer '%s' callback failed", self.name)
            if self._owner is not None:
                self._owner._worker_terminal(self, self._generation)
        else:
            if self._owner is not None and completed:
                self._owner._worker_terminal(self, self._generation)
        finally:
            self._cmd_cancel = True
            self.cancel_event.set()
            self.event.set()
            if standalone and self.publish_callback is not None:
                self.publish_callback(enabled=False)
            if self._owner is not None:
                self._owner._worker_finished(self)


class GenericTimerClass:
    """A race-safe, single-execution timer with plugin/RPC support."""

    def __init__(
            self,
            name: str,
            wait_seconds: float,
            function: Callable,
            args: Optional[list] = None,
            kwargs: Optional[dict] = None):
        self.timer_thread = None
        self.args = args if args is not None else []
        self.kwargs = kwargs if kwargs is not None else {}
        self._wait_seconds = wait_seconds
        self._start_time = 0.0
        self._deadline = None
        self._function = lambda iteration, *largs, **lkwargs: function(
            *largs,
            **lkwargs,
        )
        self._iterations = 1
        self._name = name
        self._lock = threading.RLock()
        self._generation = 0
        self._enabled = False
        self._closed = False
        self._workers = set()
        self._publish_core()

    def _active_worker_locked(self, worker, generation) -> bool:
        return (
            self._enabled
            and not self._closed
            and self.timer_thread is worker
            and self._generation == generation
            and not worker.cancel_event.is_set()
        )

    def _invoke(self, worker, generation: int, iteration: int) -> bool:
        # Holding the re-entrant lock makes callback admission atomic with
        # replacement. A callback may still cancel or restart its own timer.
        with self._lock:
            if not self._active_worker_locked(worker, generation):
                return False
            self._function(
                iteration,
                *self.args,
                **self.kwargs,
            )
            return True

    def _iteration_completed(self, worker, generation: int) -> bool:
        with self._lock:
            if not self._active_worker_locked(worker, generation):
                return False
            self._deadline = monotonic() + self._wait_seconds
            return True

    def _worker_terminal(self, worker, generation: int) -> None:
        with self._lock:
            if not self._active_worker_locked(worker, generation):
                return
            self._enabled = False
            self._deadline = None
            self._publish_core(enabled=False)

    def _worker_finished(self, worker) -> None:
        with self._lock:
            self._workers.discard(worker)

    @plugin.tag
    def start(
            self,
            wait_seconds: Optional[float] = None,
            restart: bool = True):
        """Start the timer, atomically replacing an active generation by default."""
        with self._lock:
            if self._closed:
                logger.info("Timer '%s' is closed; ignoring start command", self._name)
                return
            if self._enabled and not restart:
                logger.info("Timer '%s' is active; ignoring start command", self._name)
                return

            if wait_seconds is not None:
                self._wait_seconds = wait_seconds

            previous = self.timer_thread if self._enabled else None
            self._generation += 1
            generation = self._generation
            if previous is not None:
                previous.cancel()

            self._start_time = monotonic()
            self._deadline = self._start_time + self._wait_seconds
            worker = MultiTimer(
                self._wait_seconds,
                self._iterations,
                self._function,
                self.args,
                self.kwargs,
                owner=self,
                generation=generation,
                first_deadline=self._deadline,
            )
            worker.daemon = True
            if self._name is not None:
                worker.name = self._name
            self.timer_thread = worker
            self._workers.add(worker)
            self._enabled = True
            self._publish_core(enabled=True)
            worker.start()

    @plugin.tag
    def cancel(self):
        """Cancel the active generation."""
        with self._lock:
            if not self._enabled:
                return
            worker = self.timer_thread
            self._generation += 1
            self._enabled = False
            self._deadline = None
            if worker is not None:
                worker.cancel()
            self._publish_core(enabled=False)

    def cancel_generation(self, worker):
        """Cancel one worker without affecting a newer generation."""
        with self._lock:
            if self._enabled and self.timer_thread is worker:
                self.cancel()
            else:
                worker.cancel()

    @plugin.tag
    def toggle(self):
        """Toggle between active and disabled states."""
        if self.is_alive():
            self.cancel()
        else:
            self.start()

    @plugin.tag
    def trigger(self):
        """Trigger the active generation immediately."""
        with self._lock:
            if self._enabled and self.timer_thread is not None:
                self.timer_thread.trigger()

    @plugin.tag
    def is_alive(self) -> bool:
        """Return whether a timer generation is logically active."""
        with self._lock:
            return self._enabled

    @plugin.tag
    def get_timeout(self) -> float:
        """Return the configured timeout in seconds."""
        with self._lock:
            return self._wait_seconds

    @plugin.tag
    def set_timeout(self, wait_seconds: float) -> float:
        """Set the timeout, atomically replacing an active generation."""
        with self._lock:
            if self._enabled:
                self.start(wait_seconds, restart=True)
            else:
                self._wait_seconds = wait_seconds
                self._publish_core()
        return wait_seconds

    @plugin.tag
    def publish(self):
        """Publish the current timer state."""
        self._publish_core()

    def _remaining_seconds_locked(self) -> float:
        if not self._enabled or self._deadline is None:
            return 0
        return max(0, self._deadline - monotonic())

    @plugin.tag
    def get_state(self) -> Dict[str, Any]:
        """Return the RPC-compatible timer state."""
        with self._lock:
            return {
                'enabled': self._enabled,
                'remaining_seconds': self._remaining_seconds_locked(),
                'wait_seconds': self._wait_seconds,
                'type': 'GenericTimerClass',
            }

    def _publish_core(self, enabled: Optional[bool] = None):
        if self._name is None:
            return
        state = self.get_state()
        if enabled is not None:
            state['enabled'] = enabled
        logger.debug("%s: State = %s", self._name, state)
        publishing.get_publisher().send(self._name, state)

    def close(self):
        """Permanently close this timer and join all active workers."""
        current = threading.current_thread()
        with self._lock:
            transitioned = self._enabled
            self._closed = True
            self._enabled = False
            self._deadline = None
            self._generation += 1
            workers = list(self._workers)
            for worker in workers:
                worker.cancel()
            if transitioned:
                self._publish_core(enabled=False)

        for worker in workers:
            if worker is not current:
                worker.join()


class GenericEndlessTimerClass(GenericTimerClass):
    """A fixed-delay timer that repeats until cancellation."""

    def __init__(
            self,
            name: str,
            wait_seconds_per_iteration: float,
            function: Callable,
            args=None,
            kwargs=None):
        super().__init__(
            name,
            wait_seconds_per_iteration,
            function,
            args,
            kwargs,
        )
        self._iterations = -1

    @plugin.tag
    def get_state(self) -> Dict[str, Any]:
        """Return the RPC-compatible periodic timer state."""
        with self._lock:
            return {
                'enabled': self._enabled,
                'wait_seconds_per_iteration': self._wait_seconds,
                'type': 'GenericEndlessTimerClass',
            }
