import logging
import threading
from time import monotonic

import jukebox.cfghandler
import jukebox.plugs as plugin
import jukebox.publishing as publishing
from jukebox.multitimer import GenericTimerClass


logger = logging.getLogger('jb.timers.volume_fadeout')
cfg = jukebox.cfghandler.get_handler('jukebox')

_PHASE_DISABLED = 'disabled'
_PHASE_WAITING = 'waiting'
_PHASE_FADING = 'fading'
_PHASE_WAITING_FOR_SHUTDOWN = 'waiting_for_shutdown'
_PHASE_COMPLETE = 'complete'


class VolumeFadeoutError(Exception):
    """Raised when a fadeout timer request is invalid."""


class VolumeFadeoutAndShutdown:
    """Fade volume over the final two minutes, then request shutdown."""

    MIN_TOTAL_DURATION = 120
    FADEOUT_DURATION = 120
    FADE_STEPS = 12
    STEP_SECONDS = 10

    def __init__(
            self,
            name,
            *,
            clock=monotonic,
            get_volume=None,
            set_volume=None,
            shutdown_action=None):
        self.name = name
        self.default_timeout = cfg.setndefault(
            'timers',
            'volume_fadeout',
            'default_timeout_sec',
            value=600,
        )
        self._clock = clock
        self._get_volume = (
            get_volume
            if get_volume is not None
            else lambda: plugin.call('volume', 'ctrl', 'get_volume')
        )
        self._set_volume = (
            set_volume
            if set_volume is not None
            else lambda volume: plugin.call(
                'volume',
                'ctrl',
                'set_volume',
                args=[volume],
            )
        )
        self._shutdown_action = (
            shutdown_action
            if shutdown_action is not None
            else lambda: plugin.call_ignore_errors('host', 'shutdown')
        )
        self._lock = threading.RLock()
        self._timer = GenericTimerClass(None, self.default_timeout, self._on_timer)
        self._generation = 0
        self._worker_generations = {}
        self._enabled = False
        self._shutdown_latched = False
        self._phase = _PHASE_DISABLED
        self.start_time = None
        self.total_duration = None
        self.current_volume = None
        self.fadeout_started = False
        self._final_deadline = None
        self._fade_deadline = None
        self._next_step = 0
        self._error = None
        self._publish_locked()

    @property
    def timer_thread(self):
        """Return the current one-shot worker for shutdown integration."""
        return self._timer.timer_thread

    @staticmethod
    def _validate_duration(wait_seconds):
        if isinstance(wait_seconds, bool):
            raise VolumeFadeoutError('Duration must be a number of seconds')
        try:
            duration = float(wait_seconds)
        except (TypeError, ValueError) as error:
            raise VolumeFadeoutError(
                'Duration must be a number of seconds',
            ) from error
        if duration < VolumeFadeoutAndShutdown.MIN_TOTAL_DURATION:
            raise VolumeFadeoutError(
                'Duration must be at least '
                f'{VolumeFadeoutAndShutdown.MIN_TOTAL_DURATION} seconds',
            )
        if duration.is_integer():
            return int(duration)
        return duration

    def _is_current_locked(self, generation):
        return (
            self._enabled
            and not self._shutdown_latched
            and generation == self._generation
        )

    def _schedule(self, deadline, generation):
        delay = max(0, deadline - self._clock())
        self._timer.start(delay, restart=True)
        worker = self._timer.timer_thread
        with self._lock:
            current = self._is_current_locked(generation)
            if current:
                self._worker_generations[worker] = generation
        if not current:
            self._timer.cancel_generation(worker)

    def _remaining_seconds_locked(self):
        if not self._enabled or self._final_deadline is None:
            return 0
        return max(0, self._final_deadline - self._clock())

    def _active_state_locked(self):
        elapsed = max(0, self._clock() - self.start_time)
        progress = min(
            100,
            elapsed / self.total_duration * 100,
        )
        return {
            'enabled': True,
            'type': 'VolumeFadoutAndShutdown',
            'total_duration': self.total_duration,
            'remaining_seconds': self._remaining_seconds_locked(),
            'progress_percent': progress,
            'fadeout_started': self.fadeout_started,
            'error': self._error,
        }

    @plugin.tag
    def start(self, wait_seconds=None, restart: bool = True):
        """Start or atomically replace the fadeout timer."""
        duration = self._validate_duration(
            self.default_timeout if wait_seconds is None else wait_seconds,
        )
        with self._lock:
            if self._enabled and not restart:
                return
            self._generation += 1
            generation = self._generation
            self._worker_generations.clear()
            self._enabled = True
            self._shutdown_latched = False
            self._phase = _PHASE_WAITING
            self.start_time = self._clock()
            self.total_duration = duration
            self.current_volume = None
            self.fadeout_started = False
            self._final_deadline = self.start_time + duration
            self._fade_deadline = (
                self._final_deadline - self.FADEOUT_DURATION
            )
            self._next_step = 0
            self._error = None
            self._publish_locked()

        if duration == self.FADEOUT_DURATION:
            self._begin_fade(generation)
        else:
            self._schedule(self._fade_deadline, generation)

    def _begin_fade(self, generation):
        volume = None
        error_message = None
        try:
            volume = max(0, float(self._get_volume()))
        except Exception as error:
            logger.exception('Unable to read volume; fadeout will be skipped')
            error_message = (
                f'{error.__class__.__name__}: {error}'
            )

        with self._lock:
            if not self._is_current_locked(generation):
                return
            self.fadeout_started = True
            if error_message is not None:
                self._phase = _PHASE_WAITING_FOR_SHUTDOWN
                self._error = error_message
                deadline = self._final_deadline
            else:
                self._phase = _PHASE_FADING
                self.current_volume = volume
                self._next_step = 0
                deadline = (
                    self._fade_deadline + self.STEP_SECONDS
                )
            self._publish_locked()
        self._schedule(deadline, generation)

    def _target_volume_locked(self):
        remaining_steps = self.FADE_STEPS - self._next_step - 1
        return max(
            0,
            int(self.current_volume * remaining_steps / (self.FADE_STEPS - 1)),
        )

    def _fade_step(self, generation):
        with self._lock:
            if not self._is_current_locked(generation):
                return
            target_volume = self._target_volume_locked()

        error_message = None
        try:
            self._set_volume(target_volume)
        except Exception as error:
            logger.exception(
                'Unable to set fadeout volume to %s; continuing',
                target_volume,
            )
            error_message = f'{error.__class__.__name__}: {error}'

        request_shutdown = False
        next_deadline = None
        with self._lock:
            if not self._is_current_locked(generation):
                return
            if error_message is not None:
                self._error = error_message
            self._next_step += 1
            self._publish_locked()
            if self._next_step == self.FADE_STEPS:
                request_shutdown = self._complete_locked()
            else:
                next_deadline = (
                    self._fade_deadline
                    + (self._next_step + 1) * self.STEP_SECONDS
                )

        if next_deadline is not None:
            self._schedule(next_deadline, generation)
        if request_shutdown:
            self._request_shutdown()

    def _complete_locked(self):
        if self._shutdown_latched:
            return False
        self._shutdown_latched = True
        self._enabled = False
        self._phase = _PHASE_COMPLETE
        self._generation += 1
        self._publish_locked()
        return True

    def _request_shutdown(self):
        logger.info('Fadeout complete; initiating shutdown')
        self._shutdown_action()

    def _on_timer(self):
        worker = threading.current_thread()
        with self._lock:
            generation = self._worker_generations.pop(worker, None)
            if (
                    generation is None
                    or not self._is_current_locked(generation)):
                return
            phase = self._phase

        if phase == _PHASE_WAITING:
            self._begin_fade(generation)
        elif phase == _PHASE_FADING:
            self._fade_step(generation)
        elif phase == _PHASE_WAITING_FOR_SHUTDOWN:
            with self._lock:
                if not self._is_current_locked(generation):
                    return
                request_shutdown = self._complete_locked()
            if request_shutdown:
                self._request_shutdown()

    def _reset_locked(self):
        self._enabled = False
        self._shutdown_latched = False
        self._phase = _PHASE_DISABLED
        self.start_time = None
        self.total_duration = None
        self.current_volume = None
        self.fadeout_started = False
        self._final_deadline = None
        self._fade_deadline = None
        self._next_step = 0
        self._error = None
        self._worker_generations.clear()

    @plugin.tag
    def cancel(self):
        """Cancel all future fade and shutdown actions."""
        with self._lock:
            if not self._enabled:
                return
            self._generation += 1
            self._reset_locked()
            self._publish_locked()
        self._timer.cancel()

    @plugin.tag
    def is_alive(self):
        """Return whether the fadeout controller is active."""
        with self._lock:
            return self._enabled

    @plugin.tag
    def get_state(self):
        """Return the RPC-compatible fadeout state."""
        with self._lock:
            if self._enabled:
                return self._active_state_locked()
            return {
                'enabled': False,
                'type': 'VolumeFadoutAndShutdown',
                'total_duration': None,
                'remaining_seconds': 0,
                'progress_percent': 0,
                'error': None,
            }

    def _publish_locked(self):
        state = self.get_state()
        logger.debug('%s: State = %s', self.name, state)
        publishing.get_publisher().send(self.name, state)

    @plugin.tag
    def get_config(self):
        """Return fadeout timer configuration."""
        return {
            'default_timeout': self.default_timeout,
            'min_duration': self.MIN_TOTAL_DURATION,
            'fadeout_duration': self.FADEOUT_DURATION,
        }

    def close(self):
        """Stop timer workers without requesting shutdown."""
        with self._lock:
            transitioned = self._enabled
            self._generation += 1
            self._reset_locked()
            if transitioned:
                self._publish_locked()
        self._timer.cancel()
        self._timer.close()


# Compatibility for callers and the public state type predating the typo fix.
VolumeFadoutAndShutdown = VolumeFadeoutAndShutdown
