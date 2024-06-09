import time
import os
import logging
import threading
import json
import jukebox.cfghandler


NO_SEEK_IF_NEAR_START_END_CUTOFF = 5

logger = logging.getLogger('jb.PlayerMPD.ResumePositionTracker')
cfg = jukebox.cfghandler.get_handler('jukebox')


def play_target_to_key(play_target) -> str:
    """
    Play targets encode how the current playlist was constructed.
    play_target_to_key converts this information into a json-serializable string
    """
    return '|'.join([str(x) for x in play_target])


class ResumePositionTracker:
    """
    Keeps track of playlist and in-song position for played single tracks,
    albums or folders.
    Syncs to disk every at the configured interval and on all relevant user input
    (e.g. card swipes, prev, next, ...).
    Provides methods to retrieve the stored values to resume playing.
    """

    _last_flush_timestamp: float = 0
    _last_json: str = ''

    def __init__(self):
        self._path = cfg.getn('playermpd', 'resume', 'file',
                              default='../../shared/logs/resume_positions.json')
        self._flush_interval = cfg.getn('playermpd', 'resume', 'flush_interval_seconds',
                                        default=30)
        self.resume_by_default = cfg.getn('playermpd', 'resume', 'resume_by_default',
                                        default=False)
        self._lock = threading.RLock()
        self._tmp_path = self._path + '.tmp'
        self._current_play_target = None
        with self._lock:
            self._load()

    def _load(self):
        logger.debug(f'Loading from {self._path}')
        try:
            with open(self._path) as f:
                d = json.load(f)
        except FileNotFoundError:
            logger.debug('File not found, assuming empty list')
            self._play_targets = {}
            self.flush()
            return
        self._play_targets = d['positions_by_play_target']
        logger.debug(f'Loaded {len(self._play_targets.keys())} saved target play positions')

    def set_current_play_target(self, play_target):
        with self._lock:
            self._current_play_target = play_target_to_key(play_target)

    def is_current_play_target(self, play_target):
        return self._current_play_target == play_target

    def get_playlist_position_by_play_target(self, play_target):
        return self._play_targets.get(play_target_to_key(play_target), {}).get('playlist_position')

    def get_seek_position_by_play_target(self, play_target):
        return self._play_targets.get(play_target_to_key(play_target), {}).get('seek_position')

    def handle_mpd_status(self, status):
        if not self._current_play_target:
            return
        playlist_len = int(status.get('playlistlength', -1))
        playlist_pos = int(status.get('pos', 0))
        elapsed = float(status.get('elapsed', 0))
        duration = float(status.get('duration', 0))
        is_end_of_playlist = playlist_pos == playlist_len - 1
        is_end_of_track = duration - elapsed < NO_SEEK_IF_NEAR_START_END_CUTOFF
        if status.get('state') == 'stop' and is_end_of_playlist and is_end_of_track:
            # If we are at the end of the playlist,
            # we want to restart the playlist the next time the card is present.
            # Therefore, delete all resume information:
            if self._current_play_target in self._play_targets:
                with self._lock:
                    del self._play_targets[self._current_play_target]
            return
        with self._lock:
            if self._current_play_target not in self._play_targets:
                self._play_targets[self._current_play_target] = {}
            self._play_targets[self._current_play_target]['playlist_position'] = playlist_pos
        if (elapsed < NO_SEEK_IF_NEAR_START_END_CUTOFF
             or ((duration - elapsed) < NO_SEEK_IF_NEAR_START_END_CUTOFF)):
            # restart song next time:
            elapsed = 0
        with self._lock:
            if self._current_play_target not in self._play_targets:
                self._play_targets[self._current_play_target] = {}
            self._play_targets[self._current_play_target]['seek_position'] = elapsed
        self._flush_if_necessary()

    def _flush_if_necessary(self):
        now = time.time()
        if self._last_flush_timestamp + self._flush_interval < now:
            return self.flush()

    def flush(self):
        """
        Forces writing the current play positition information
        to disk after checking that there were actual changes.
        """
        with self._lock:
            self._last_flush_timestamp = time.time()
            new_json = json.dumps(
                {
                    'positions_by_play_target': self._play_targets,
                }, indent=2, sort_keys=True)
            if self._last_json == new_json:
                return
            with open(self._tmp_path, 'w') as f:
                f.write(new_json)
            os.rename(self._tmp_path, self._path)
            self._last_json = new_json
            logger.debug(f'Flushed state to {self._path}')

    def __del__(self):
        self.flush()
