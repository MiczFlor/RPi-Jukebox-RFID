# RPi-Jukebox-RFID Version 3
# Copyright (c) See file LICENSE in project root folder

import time
import os
import re
import logging
import threading
import jukebox.plugs as plugin


logger = logging.getLogger('jb.timers.idle_shutdown_timer')
SSH_CHILD_RE = re.compile(r'sshd: [^/].*')
PATHS = ['shared/settings',
         'shared/audiofolders']


def get_seconds_since_boot():
    # We may not have a stable clock source when there is no network
    # connectivity (yet). As we only need to measure the relative time which
    # has passed, we can just calculate based on the seconds since boot.
    with open('/proc/uptime') as f:
        line = f.read()
    seconds_since_boot, _ = line.split(' ', 1)
    return float(seconds_since_boot)


class IdleShutdownTimer(threading.Thread):
    """
    Shuts down the system if no activity is detected.
    The following activity is covered:
        - playing music
        - active SSH sessions
        - changes of configs or audio content

    Note: This does not use one of the generic timers as there don't seem
    to be any benefits here. The shutdown timer is kind of special in that it
    is a timer which is expected *not* to fire most of the time, because some
    activity would restart it. Using threading.Thread directly allows us to
    keep using a single, persistent thread.
    """
    shutdown_after_seconds: int
    last_activity: float = 0
    files_num_entries: int = 0
    files_latest_mtime: float = 0
    running: bool = True
    last_player_status = None
    SLEEP_INTERVAL_SECONDS: int = 10

    def __init__(self, timeout_seconds):
        super().__init__(name=__class__.__name__)
        self.shutdown_after_seconds = timeout_seconds
        self.base_path = os.path.join(os.path.dirname(__file__), '..', '..', '..', '..')
        self.record_activity()
        logger.debug('Started IdleShutdownTimer')

    def record_activity(self):
        self.last_activity = get_seconds_since_boot()

    def check(self):
        if self.last_activity + self.shutdown_after_seconds > get_seconds_since_boot():
            return
        logger.info('No player activity, starting further checks')
        if self._has_active_ssh_sessions():
            logger.info('Active SSH sessions found, will not shutdown now')
            self.record_activity()
            return
        if self._has_changed_files():
            logger.info('Changes files found, will not shutdown now')
            self.record_activity()
            return
        logger.info(f'No activity since {self.shutdown_after_seconds} seconds, shutting down')
        plugin.call_ignore_errors('host', 'shutdown')

    def run(self):
        # We need this once as a baseline:
        self._has_changed_files()
        # We rely on playerstatus being sent in regular intervals. If this
        # is no longer the case at some point, we would need an additional
        # timer thread.
        while self.running:
            time.sleep(self.SLEEP_INTERVAL_SECONDS)
            player_status = plugin.call('player', 'ctrl', 'playerstatus')
            if player_status == self.last_player_status:
                self.check()
            else:
                self.record_activity()
            self.last_player_status = player_status.copy()

    def cancel(self):
        self.running = False

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
