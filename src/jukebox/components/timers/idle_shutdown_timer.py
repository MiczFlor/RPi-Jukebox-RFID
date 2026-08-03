import logging
import os
import re
import stat
import threading
from time import monotonic

import jukebox.cfghandler
import jukebox.plugs as plugin
import jukebox.publishing as publishing
from jukebox.multitimer import GenericEndlessTimerClass


logger = logging.getLogger('jb.timers.idle_shutdown_timer')
cfg = jukebox.cfghandler.get_handler('jukebox')

SSH_CHILD_RE = re.compile(r'sshd: [^/].*')
PATHS = ['shared/settings', 'shared/audiofolders']

IDLE_SHUTDOWN_TIMER_MIN_TIMEOUT_SECONDS = 60
IDLE_CHECK_INTERVAL = 10
FILESYSTEM_GRACE_SECONDS = 60

_PHASE_DISABLED = 'disabled'
_PHASE_NEEDS_BASELINE = 'needs_baseline'
_PHASE_OTHER_ACTIVITY = 'other_activity'
_PHASE_COUNTDOWN = 'countdown'
_PHASE_GRACE = 'grace'


class FilesystemSnapshotError(RuntimeError):
    """Raised when a stable filesystem fingerprint cannot be collected."""


def playback_active():
    """Return whether audio playback is active."""
    status = plugin.call('player', 'ctrl', 'playerstatus')
    return status['state'] == 'play'


def ssh_activity():
    """Return whether an interactive SSH child process is active."""
    with os.scandir('/proc') as proc_entries:
        for entry in proc_entries:
            if not entry.name.isdigit():
                continue
            try:
                with open(
                        os.path.join(entry.path, 'cmdline'),
                        encoding='utf-8',
                        errors='replace') as cmdline_file:
                    cmdline = cmdline_file.read().replace('\0', ' ')
            except (FileNotFoundError, PermissionError, ProcessLookupError):
                continue
            if SSH_CHILD_RE.match(cmdline):
                return True
    return False


def _entry_type(stat_result):
    mode = stat_result.st_mode
    if stat.S_ISDIR(mode):
        return 'directory'
    if stat.S_ISREG(mode):
        return 'file'
    if stat.S_ISLNK(mode):
        return 'symlink'
    return 'other'


def filesystem_fingerprint(paths):
    """Return a stable fingerprint for configured roots and their entries."""
    fingerprint = []

    for root_index, root in enumerate(paths):
        root_key = str(root_index)
        try:
            root_stat = os.lstat(root)
        except FileNotFoundError:
            fingerprint.append((root_key, 'missing', 0, 0))
            continue
        except OSError as error:
            raise FilesystemSnapshotError(str(error)) from error

        fingerprint.append((
            root_key,
            _entry_type(root_stat),
            root_stat.st_size,
            root_stat.st_mtime_ns,
        ))

        def raise_walk_error(error):
            raise FilesystemSnapshotError(str(error)) from error

        try:
            for current_root, directories, files in os.walk(
                    root,
                    followlinks=False,
                    onerror=raise_walk_error):
                for name in directories + files:
                    path = os.path.join(current_root, name)
                    relative_path = os.path.relpath(path, root)
                    entry_stat = os.lstat(path)
                    fingerprint.append((
                        f'{root_key}/{relative_path}',
                        _entry_type(entry_stat),
                        entry_stat.st_size,
                        entry_stat.st_mtime_ns,
                    ))
        except (FileNotFoundError, PermissionError, ProcessLookupError) as error:
            raise FilesystemSnapshotError(str(error)) from error
        except OSError as error:
            raise FilesystemSnapshotError(str(error)) from error

    return tuple(sorted(fingerprint))


class IdleShutdownTimer:
    """Monitor host activity and request shutdown after a verified idle period."""

    def __init__(
            self,
            package: str,
            idle_timeout,
            *,
            clock=monotonic,
            playback_detector=playback_active,
            ssh_detector=ssh_activity,
            snapshotter=None,
            paths=None,
            check_interval=IDLE_CHECK_INTERVAL,
            grace_seconds=FILESYSTEM_GRACE_SECONDS,
            shutdown_action=None):
        self.package = package
        self.name = f'{package}.timer_idle_shutdown'
        self._clock = clock
        self._playback_detector = playback_detector
        self._ssh_detector = ssh_detector
        self._paths = paths if paths is not None else self._default_paths()
        self._snapshotter = (
            snapshotter
            if snapshotter is not None
            else lambda: filesystem_fingerprint(self._paths)
        )
        self._grace_seconds = grace_seconds
        self._shutdown_action = (
            shutdown_action
            if shutdown_action is not None
            else lambda: plugin.call_ignore_errors('host', 'shutdown')
        )
        self._lock = threading.RLock()
        self._wait_seconds = 0
        self._deadline = None
        self._baseline = None
        self._enabled = False
        self._running = False
        self._shutdown_latched = False
        self._phase = _PHASE_DISABLED
        self._detector_error_logged = False
        self._snapshot_error_logged = False
        self._controller_generation = 0
        self._monitor = GenericEndlessTimerClass(
            name=None,
            wait_seconds_per_iteration=check_interval,
            function=self._poll,
        )

        try:
            startup_timeout = self._validate_timeout(
                idle_timeout,
                allow_disabled=True,
            )
        except ValueError:
            logger.warning(
                'Invalid timers.idle_shutdown.timeout_sec value %r; '
                'idle shutdown remains disabled',
                idle_timeout,
            )
            startup_timeout = 0

        with self._lock:
            self._wait_seconds = startup_timeout
            if startup_timeout:
                generation = self._begin_locked(startup_timeout)
            else:
                self._publish_locked()
                generation = None
        if generation is not None:
            self._start_monitor(generation)

    @staticmethod
    def _default_paths():
        repository_root = os.path.abspath(os.path.join(
            os.path.dirname(__file__),
            '..',
            '..',
            '..',
            '..',
        ))
        return [os.path.join(repository_root, path) for path in PATHS]

    @staticmethod
    def _validate_timeout(wait_seconds, *, allow_disabled=False):
        if isinstance(wait_seconds, bool):
            raise ValueError('wait_seconds must be an integer number of seconds')
        try:
            timeout = int(wait_seconds)
        except (TypeError, ValueError) as error:
            raise ValueError(
                'wait_seconds must be an integer number of seconds',
            ) from error
        if timeout == 0 and allow_disabled:
            return 0
        if timeout < IDLE_SHUTDOWN_TIMER_MIN_TIMEOUT_SECONDS:
            raise ValueError(
                'wait_seconds must be at least '
                f'{IDLE_SHUTDOWN_TIMER_MIN_TIMEOUT_SECONDS} seconds',
            )
        return timeout

    @property
    def timer_thread(self):
        """Return the periodic worker for legacy shutdown integration."""
        return self._monitor.timer_thread

    def _take_snapshot_locked(self):
        try:
            snapshot = self._snapshotter()
        except Exception as error:
            if not self._snapshot_error_logged:
                logger.warning(
                    'Filesystem activity check failed; postponing idle shutdown: '
                    '%s: %s',
                    error.__class__.__name__,
                    error,
                )
                self._snapshot_error_logged = True
            return None
        self._snapshot_error_logged = False
        return snapshot

    def _begin_locked(self, wait_seconds):
        self._controller_generation += 1
        now = self._clock()
        self._wait_seconds = wait_seconds
        self._enabled = True
        self._running = False
        self._shutdown_latched = False
        self._deadline = now + wait_seconds
        self._baseline = self._take_snapshot_locked()
        if self._baseline is None:
            self._phase = _PHASE_NEEDS_BASELINE
        else:
            self._phase = _PHASE_COUNTDOWN
            self._running = True
        self._publish_locked()
        return self._controller_generation

    def _start_monitor(self, generation):
        self._monitor.start(restart=True)
        worker = self._monitor.timer_thread
        with self._lock:
            stale = (
                not self._enabled
                or generation != self._controller_generation
            )
        if stale and worker is not None:
            self._monitor.cancel_generation(worker)

    def _remaining_seconds_locked(self):
        if not self._enabled or not self._running or self._deadline is None:
            return 0
        return max(0, self._deadline - self._clock())

    @plugin.tag
    def start(self, wait_seconds: int, restart: bool = True):
        """Enable monitoring and persist a new idle timeout."""
        timeout = self._validate_timeout(wait_seconds)
        with self._lock:
            if self._enabled and not restart:
                return
            cfg.setn(
                'timers',
                'idle_shutdown',
                'timeout_sec',
                value=timeout,
            )
            generation = self._begin_locked(timeout)
        self._start_monitor(generation)

    @plugin.tag
    def cancel(self):
        """Disable idle shutdown and persist the disabled configuration."""
        with self._lock:
            cfg.setn(
                'timers',
                'idle_shutdown',
                'timeout_sec',
                value=0,
            )
            transitioned = self._enabled
            self._enabled = False
            self._controller_generation += 1
            self._running = False
            self._deadline = None
            self._baseline = None
            self._phase = _PHASE_DISABLED
            if transitioned:
                self._publish_locked()
        self._monitor.cancel()

    @plugin.tag
    def get_state(self):
        """Return the RPC-compatible idle shutdown state."""
        with self._lock:
            return {
                'enabled': self._enabled,
                'running': self._running,
                'remaining_seconds': self._remaining_seconds_locked(),
                'wait_seconds': self._wait_seconds,
            }

    def _publish_locked(self):
        state = self.get_state()
        logger.debug('%s: State = %s', self.name, state)
        publishing.get_publisher().send(self.name, state)

    def _mark_other_activity_locked(self, now):
        transitioned = (
            self._running
            or self._phase != _PHASE_OTHER_ACTIVITY
        )
        self._running = False
        self._phase = _PHASE_OTHER_ACTIVITY
        self._deadline = now + self._wait_seconds
        self._baseline = None
        if transitioned:
            self._publish_locked()

    def _capture_baseline_locked(self, now):
        snapshot = self._take_snapshot_locked()
        if snapshot is None:
            transitioned = self._phase != _PHASE_NEEDS_BASELINE
            self._running = False
            self._phase = _PHASE_NEEDS_BASELINE
            self._deadline = now + self._wait_seconds
            if transitioned:
                self._publish_locked()
            return
        self._baseline = snapshot
        self._running = True
        self._phase = _PHASE_COUNTDOWN
        self._deadline = now + self._wait_seconds
        self._publish_locked()

    def _postpone_for_detector_error_locked(self, now, errors):
        if not self._detector_error_logged:
            error = errors[0]
            logger.warning(
                'Idle activity detector failed; postponing shutdown: %s: %s',
                error.__class__.__name__,
                error,
            )
            self._detector_error_logged = True
        self._mark_other_activity_locked(now)

    def _check_filesystem_locked(self, now):
        snapshot = self._take_snapshot_locked()
        if snapshot is None:
            self._baseline = None
            self._running = False
            self._phase = _PHASE_NEEDS_BASELINE
            self._deadline = now + self._wait_seconds
            self._publish_locked()
            return False
        if self._baseline != snapshot:
            self._baseline = snapshot
            self._running = True
            self._phase = _PHASE_COUNTDOWN
            self._deadline = now + self._wait_seconds
            self._publish_locked()
            return False
        return True

    def _detect_activity(self):
        detector_errors = []
        playback = False
        ssh = False
        try:
            playback = bool(self._playback_detector())
        except Exception as error:
            detector_errors.append(error)
        try:
            ssh = bool(self._ssh_detector())
        except Exception as error:
            detector_errors.append(error)
        return playback, ssh, detector_errors

    def _advance_locked(self, now, playback, ssh):
        if playback or ssh:
            self._mark_other_activity_locked(now)
            return False

        if self._phase in (
                _PHASE_OTHER_ACTIVITY,
                _PHASE_NEEDS_BASELINE):
            self._capture_baseline_locked(now)
            return False

        if now < self._deadline:
            return False

        if not self._check_filesystem_locked(now):
            return False

        if self._phase == _PHASE_COUNTDOWN:
            self._phase = _PHASE_GRACE
            self._deadline = now + self._grace_seconds
            self._publish_locked()
            return False

        self._shutdown_latched = True
        self._enabled = False
        self._running = False
        self._deadline = None
        self._phase = _PHASE_DISABLED
        self._monitor.cancel()
        self._publish_locked()
        return True

    def _poll(self):
        playback, ssh, detector_errors = self._detect_activity()
        with self._lock:
            if not self._enabled or self._shutdown_latched:
                return
            now = self._clock()
            if detector_errors:
                self._postpone_for_detector_error_locked(
                    now,
                    detector_errors,
                )
                return
            self._detector_error_logged = False
            request_shutdown = self._advance_locked(now, playback, ssh)

        if request_shutdown:
            logger.info('No activity after verification grace period; shutting down')
            self._shutdown_action()

    def close(self):
        """Stop monitor workers without changing persisted configuration."""
        with self._lock:
            transitioned = self._enabled
            self._enabled = False
            self._controller_generation += 1
            self._running = False
            self._deadline = None
            self._baseline = None
            self._phase = _PHASE_DISABLED
            if transitioned:
                self._publish_locked()
        self._monitor.cancel()
        self._monitor.close()
