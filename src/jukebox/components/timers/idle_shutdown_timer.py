# RPi-Jukebox-RFID Version 3
# Copyright (c) See file LICENSE in project root folder

import os
import re
import logging
import jukebox.cfghandler
import jukebox.plugs as plugin
from jukebox.multitimer import (GenericEndlessTimerClass, GenericMultiTimerClass)


logger = logging.getLogger('jb.timers.idle_shutdown_timer')
cfg = jukebox.cfghandler.get_handler('jukebox')

SSH_CHILD_RE = re.compile(r'sshd: [^/].*')
PATHS = ['shared/settings',
         'shared/audiofolders']

IDLE_SHUTDOWN_TIMER_MIN_TIMEOUT_SECONDS = 60
EXTEND_IDLE_TIMEOUT = 60
IDLE_CHECK_INTERVAL = 10


def get_seconds_since_boot():
    # We may not have a stable clock source when there is no network
    # connectivity (yet). As we only need to measure the relative time which
    # has passed, we can just calculate based on the seconds since boot.
    with open('/proc/uptime') as f:
        line = f.read()
    seconds_since_boot, _ = line.split(' ', 1)
    return float(seconds_since_boot)


class IdleShutdownTimer:
    def __init__(self, package: str, idle_timeout: int) -> None:
        self.private_timer_idle_shutdown = None
        self.private_timer_idle_check = None
        self.idle_timeout = 0
        self.package = package
        self.idle_check_interval = IDLE_CHECK_INTERVAL

        self.set_idle_timeout(idle_timeout)
        self.init_idle_shutdown()
        self.init_idle_check()

    def set_idle_timeout(self, idle_timeout):
        try:
            self.idle_timeout = int(idle_timeout)
        except ValueError:
            logger.warning(f'invalid timers.idle_shutdown.timeout_sec value {repr(idle_timeout)}')

        if self.idle_timeout < IDLE_SHUTDOWN_TIMER_MIN_TIMEOUT_SECONDS:
            logger.info('disabling idle shutdown timer; set '
                        'timers.idle_shutdown.timeout_sec to at least '
                        f'{IDLE_SHUTDOWN_TIMER_MIN_TIMEOUT_SECONDS} seconds to enable')
            self.idle_timeout = 0

    # Using GenericMultiTimerClass instead of GenericTimerClass as it supports classes rather than functions
    # Calling GenericMultiTimerClass with iterations=1 is the same as GenericTimerClass
    def init_idle_shutdown(self):
        self.private_timer_idle_shutdown = GenericMultiTimerClass(
            name=f"{self.package}.private_timer_idle_shutdown",
            iterations=1,
            wait_seconds_per_iteration=self.idle_timeout,
            callee=IdleShutdown
        )
        self.private_timer_idle_shutdown.__doc__ = "Timer to shutdown after system is idle for a given time"
        plugin.register(self.private_timer_idle_shutdown, name='private_timer_idle_shutdown', package=self.package)

    # Regularly check if player has activity, if not private_timer_idle_check will start/cancel private_timer_idle_shutdown
    def init_idle_check(self):
        idle_check_timer_instance = IdleCheck()
        self.private_timer_idle_check = GenericEndlessTimerClass(
            name=f"{self.package}.private_timer_idle_check",
            wait_seconds_per_iteration=self.idle_check_interval,
            function=idle_check_timer_instance
        )
        self.private_timer_idle_check.__doc__ = 'Timer to check if system is idle'
        if self.idle_timeout:
            self.private_timer_idle_check.start()

        plugin.register(self.private_timer_idle_check, name='private_timer_idle_check', package=self.package)

    @plugin.tag
    def start(self, wait_seconds: int):
        """Sets idle_shutdown timeout_sec stored in jukebox.yaml"""
        cfg.setn('timers', 'idle_shutdown', 'timeout_sec', value=wait_seconds)
        plugin.call_ignore_errors('timers', 'private_timer_idle_check', 'start')

    @plugin.tag
    def cancel(self):
        """Cancels all idle timers and disables idle shutdown in jukebox.yaml"""
        plugin.call_ignore_errors('timers', 'private_timer_idle_check', 'cancel')
        plugin.call_ignore_errors('timers', 'private_timer_idle_shutdown', 'cancel')
        cfg.setn('timers', 'idle_shutdown', 'timeout_sec', value=0)

    @plugin.tag
    def get_state(self):
        """Returns the current state of Idle Shutdown"""
        idle_check_state = plugin.call_ignore_errors('timers', 'private_timer_idle_check', 'get_state')
        idle_shutdown_state = plugin.call_ignore_errors('timers', 'private_timer_idle_shutdown', 'get_state')

        return {
            'enabled': idle_check_state['enabled'],
            'running': idle_shutdown_state['enabled'],
            'remaining_seconds': idle_shutdown_state['remaining_seconds'],
            'wait_seconds': idle_shutdown_state['wait_seconds_per_iteration'],
        }


class IdleCheck:
    def __init__(self) -> None:
        self.last_player_status = plugin.call('player', 'ctrl', 'playerstatus')
        logger.debug('Started IdleCheck with initial state: {}'.format(self.last_player_status))

    # Run function
    def __call__(self):
        player_status = plugin.call('player', 'ctrl', 'playerstatus')

        if self.last_player_status == player_status:
            plugin.call_ignore_errors('timers', 'private_timer_idle_shutdown', 'start')
        else:
            plugin.call_ignore_errors('timers', 'private_timer_idle_shutdown', 'cancel')

        self.last_player_status = player_status.copy()
        return self.last_player_status


class IdleShutdown():
    files_num_entries: int = 0
    files_latest_mtime: float = 0

    def __init__(self) -> None:
        self.base_path = os.path.join(os.path.dirname(__file__), '..', '..', '..', '..')

    def __call__(self):
        logger.debug('Last checks before shutting down')
        if self._has_active_ssh_sessions():
            logger.debug('Active SSH sessions found, will not shutdown now')
            plugin.call_ignore_errors('timers', 'private_timer_idle_shutdown', 'set_timeout', args=[int(EXTEND_IDLE_TIMEOUT)])
            return
        # if self._has_changed_files():
        #     logger.debug('Changes files found, will not shutdown now')
        #     plugin.call_ignore_errors(
        #         'timers',
        #         'private_timer_idle_shutdown',
        #         'set_timeout',
        #         args=[int(EXTEND_IDLE_TIMEOUT)])
        #     return

        logger.info('No activity, shutting down')
        plugin.call_ignore_errors('timers', 'private_timer_idle_check', 'cancel')
        plugin.call_ignore_errors('timers', 'private_timer_idle_shutdown', 'cancel')
        plugin.call_ignore_errors('host', 'shutdown')

    @staticmethod
    def _has_active_ssh_sessions():
        logger.debug('Checking for SSH activity')
        with os.scandir('/proc') as proc_dir:
            for proc_path in proc_dir:
                if not proc_path.is_dir():
                    continue
                try:
                    with open(os.path.join(proc_path, 'cmdline')) as f:
                        cmdline = f.read()
                except (FileNotFoundError, PermissionError):
                    continue
                if SSH_CHILD_RE.match(cmdline):
                    return True

    def _has_changed_files(self):
        # This is a rather expensive check, but it only runs twice
        # when an idle shutdown is initiated.
        # Only when there are actual changes (file transfers via
        # SFTP, Samba, etc.), the check may run multiple times.
        logger.debug('Scanning for file changes')
        latest_mtime = 0
        num_entries = 0
        for path in PATHS:
            for root, dirs, files in os.walk(os.path.join(self.base_path, path)):
                for p in dirs + files:
                    mtime = os.stat(os.path.join(root, p)).st_mtime
                    latest_mtime = max(latest_mtime, mtime)
                    num_entries += 1

        logger.debug(f'Completed file scan ({num_entries} entries, latest_mtime={latest_mtime})')
        if self.files_latest_mtime != latest_mtime or self.files_num_entries != num_entries:
            # We compare the number of entries to have a chance to detect file
            # deletions as well.
            self.files_latest_mtime = latest_mtime
            self.files_num_entries = num_entries
            return True

        return False
