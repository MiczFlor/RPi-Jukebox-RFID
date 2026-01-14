# RPi-Jukebox-RFID Version 3
# Copyright (c) See file LICENSE in project root folder

import os
import re
from glob import iglob
import logging
import jukebox.cfghandler
import jukebox.plugs as plugin
from jukebox.multitimer import GenericEndlessTimerClass
# Use monotonic time to avoid issues with system time changes
from time import monotonic as time

logger = logging.getLogger('jb.timers.idle_shutdown_timer')
cfg = jukebox.cfghandler.get_handler('jukebox')
base_path = os.path.join(os.path.dirname(__file__), '..', '..', '..', '..')

PATHS = ['shared/settings',
         'shared/audiofolders']
SSH_CHILD_RE = re.compile(r'sshd: [^/].*')

IDLE_SHUTDOWN_TIMER_MIN_TIMEOUT_SECONDS = 60
IDLE_CHECK_INTERVAL = 10


def playback_active():
    # Returns True if audio is currently playing
    player_status = plugin.call('player', 'ctrl', 'playerstatus')
    return player_status['state'] == 'play'


def ssh_activity():
    # Returns True if there is an active SSH session
    logger.debug('Checking for SSH activity')

    for cmdline in iglob('/proc/*/cmdline'):
        try:
            with open(cmdline) as f:
                cmdline = f.read()
        except PermissionError:
            continue
        if SSH_CHILD_RE.match(cmdline):
            logger.info('SSH activity detected, resetting idle timer')
            return True
    return False


class FSWatcher:
    # Minimal filesystem watcher that needs to be polled to detect changes.
    def __init__(self, paths):
        self.paths = paths
        self.previous_state = None
        self.has_changed()  # Initialize state

    def has_changed(self):
        # Returns True if the directory state has changed since the last call/initialization.
        logger.debug('Collecting directory state')
        latest_mtime = 0
        num_entries = 0
        for path in self.paths:
            for root, dirs, files in os.walk(path):
                for p in dirs + files:
                    mtime = os.stat(os.path.join(root, p)).st_mtime
                    latest_mtime = max(latest_mtime, mtime)
                    num_entries += 1

        logger.debug(f'Completed file scan ({num_entries} entries, latest_mtime={latest_mtime})')
        has_changed = self.previous_state != (num_entries, latest_mtime)
        self.previous_state = (num_entries, latest_mtime)
        return has_changed


class IdleShutdownTimer:
    def __init__(self, package: str, idle_timeout: int) -> None:
        self.private_timer_idle_check = None
        self.idle_timeout = idle_timeout
        self.package = package
        self.last_activity_time = time()
        self.fswatcher = FSWatcher([os.path.join(base_path, path) for path in PATHS])
        self.idle_state = False  # Idle state as determined in last idle_check()

        self.init_idle_check(idle_timeout)

    def init_idle_check(self, idle_timeout):
        self.idle_timeout = int(idle_timeout)

        # Prevent bricking the system by shutting down immediately after boot
        if self.idle_timeout < IDLE_SHUTDOWN_TIMER_MIN_TIMEOUT_SECONDS:
            logger.info('disabling idle shutdown timer; set timers.idle_shutdown.timeout_sec to at least '
                        f'{IDLE_SHUTDOWN_TIMER_MIN_TIMEOUT_SECONDS} seconds to enable')
            self.idle_timeout = 0

        self.private_timer_idle_check = GenericEndlessTimerClass(
            name=f"{self.package}.private_timer_idle_check",
            wait_seconds_per_iteration=IDLE_CHECK_INTERVAL,
            function=self.idle_check
        )
        self.private_timer_idle_check.__doc__ = 'Timer to check if system is idle'
        if self.idle_timeout:
            self.private_timer_idle_check.start()

        plugin.register(self.private_timer_idle_check, name='private_timer_idle_check', package=self.package)

    def time_left(self):
        if not self.idle_timeout:
            return None
        return self.idle_timeout - (time() - self.last_activity_time)

    def idle_check(self):
        # Regularly check for activity

        # Lazily evaluate activity functions to avoid unnecessary expensive checks.
        # Note this can lead to FSWatcher.has_changed returning True once when playback and ssh go inactive, effectively
        # extending the idle timeout by one check interval. This is acceptable.
        if playback_active() or ssh_activity() or self.fswatcher.has_changed():
            self.idle_state = False
            # Be generous and mark this whole interval as active by adding IDLE_CHECK_INTERVAL
            self.last_activity_time = time() + IDLE_CHECK_INTERVAL
        else:
            self.idle_state = True
            time_left = self.time_left()
            if time_left > 0:
                logger.debug(f'No activity detected, shutting down in {int(time_left)} seconds')
            else:
                logger.debug('No activity detected, initiating shutdown sequence')
                plugin.call_ignore_errors('host', 'shutdown')

    @plugin.tag
    def start(self, wait_seconds: int):
        """Updates idle_shutdown timeout_sec (also in jukebox.yaml), starts the idle timer in case it wasn't running yet"""
        cfg.setn('timers', 'idle_shutdown', 'timeout_sec', value=wait_seconds)
        self.private_timer_idle_check.start()

    @plugin.tag
    def cancel(self):
        """Cancels the idle timer"""
        self.private_timer_idle_check.cancel()

    @plugin.tag
    def get_state(self):
        """Returns the current state of Idle Shutdown"""
        idle_check_state = self.private_timer_idle_check.get_state()

        # Field names compatible to previous version:
        return {
            'enabled': idle_check_state['enabled'],
            'running': self.idle_state,
            'remaining_seconds': self.time_left(),
        }
