"""
Display plugin for showing the current player status on an external display.

This plugin subscribes to the internal Jukebox publisher and updates the display
whenever the player status changes meaningfully.

Display updates are processed serially by a single worker thread. If multiple
updates arrive while a refresh is in progress, only the latest update is applied.
This is required for EPD/e-paper displays which cannot handle concurrent refreshes.
"""

import os
import zmq
import threading
import json
import logging
from pathlib import Path

import jukebox.plugs as plugin
import jukebox.cfghandler
import jukebox.publishing
import jukebox.utils
import components.player

from components.player.backends.coverart_cache_manager import CoverartCacheManager

logger = logging.getLogger('jb.Display')
cfg_main = jukebox.cfghandler.get_handler('jukebox')
cfg_display = jukebox.cfghandler.get_handler('display')

# Time to wait before clearing the display after a stop event.
# This avoids flickering during track/folder changes where MPD briefly reports stop.
CLEAR_DELAY_SECONDS = 2.0


def _format_status(status):
    """
    Extract display-relevant fields from the player status.
    """
    if not isinstance(status, dict):
        return None, None, 'stop', ''

    state = status.get('state', 'stop')
    title = status.get('title', '')
    artist = status.get('artist', '')
    album = status.get('album', '')
    file_path = status.get('file', '')
    repeat_info = _format_repeat(status)
    return title, artist, state, file_path, repeat_info, album


def _format_repeat(status):
    """
    Build a short repeat indicator from MPD repeat/single fields.
    """
    repeat = status.get('repeat')
    single = status.get('single')

    if repeat in (1, '1', True):
        if single in (1, '1', True):
            return 'repeat_one'
        return 'repeat_all'
    return ''


def _resolve_music_file(file_path: str):
    """
    Resolve a relative file path from playerstatus to an absolute music file path.
    Returns None for streams or invalid paths.
    """
    if not file_path:
        return None
    if file_path.startswith(('http://', 'https://', 'ftp://', 'mms://')):
        return None
    try:
        library_path = components.player.get_music_library_path()
        resolved = Path(library_path, file_path).expanduser().resolve()
        return resolved
    except Exception as e:
        logger.debug(f'Could not resolve music file {file_path}: {e}')
        return None


def _get_coverart_path_for_file(file_path: str, cache_manager):
    """
    Resolve cover art for the given player file path.
    Returns the cache filename if available, or None if unavailable/pending.
    """
    mp3_file_path = _resolve_music_file(file_path)
    if mp3_file_path is None:
        logger.debug(f'Cannot resolve coverart: {file_path} is a stream or invalid path')
        return None
    if cache_manager is None:
        logger.debug('No coverart cache manager available')
        return None

    from components.player.backends.coverart_cache_manager import CACHE_PENDING, NO_CACHE

    cache_filename = cache_manager.get_cache_filename(str(mp3_file_path))
    logger.debug(f'Coverart for {file_path}: {cache_filename}')

    if cache_filename in (CACHE_PENDING, NO_CACHE, ''):
        return None

    return cache_filename


def _get_coverart_cache_directory():
    """
    Return the absolute path to the cover art cache directory.
    """
    try:
        cache_path = cfg_main.getn('webapp', 'coverart_cache_path')
        return Path(cache_path).expanduser().resolve()
    except Exception as e:
        logger.debug(f'Could not resolve coverart cache directory: {e}')
        return None


def _resolve_coverart_path(cache_filename: str):
    """
    Resolve a cover art cache filename to an absolute file path.
    """
    if not cache_filename:
        return None
    if os.path.isabs(cache_filename):
        return cache_filename

    cache_dir = _get_coverart_cache_directory()
    if cache_dir is None:
        return None

    cover_path = cache_dir / cache_filename
    if cover_path.is_file():
        return str(cover_path)
    return None


def _create_coverart_cache_manager():
    """
    Create a dedicated CoverartCacheManager instance for the display plugin.
    """
    try:
        return CoverartCacheManager()
    except Exception as e:
        logger.error(f'Could not create display cover art cache manager: {e}')
        return None


def _create_display():
    """
    Factory for creating the configured display driver.
    """

    display_type: str = cfg_display.setndefault('display', 'type', value=None)

    if display_type == 'epd2in9b_V3':
        from .epd2in9b_V3 import Epd2in9bV3Display
        return Epd2in9bV3Display()

    if display_type == 'epd2in9b_V4':
        from .epd2in9b_V4 import Epd2in9bV4Display
        return Epd2in9bV4Display()

    if display_type == 'fb_2in8':
        from .fb_2in8 import Fb2in8Display
        framebuffer = cfg_display.setndefault('display', 'framebuffer', value='/dev/fb0')
        color_format = cfg_display.setndefault('display', 'color_format', value='rgb888')
        return Fb2in8Display(framebuffer=framebuffer, color_format=color_format)

    raise ValueError(f"Unsupported display type '{display_type}'")


class DisplaySubscriber:
    """
    Subscriber that listens to playerstatus updates and refreshes the display.

    Display updates are processed serially by a single worker thread. If multiple
    updates arrive while a refresh is in progress, only the latest update is applied.
    This is required for EPD/e-paper displays which cannot handle concurrent refreshes.
    """

    def __init__(self):
        self.ctx = zmq.Context.instance()

        self._status_sub = self.ctx.socket(zmq.SUB)
        self._status_sub.connect('inproc://PublisherToProxy')
        self._status_sub.setsockopt(zmq.SUBSCRIBE, b'playerstatus')

        self._coverart_sub = self.ctx.socket(zmq.SUB)
        self._coverart_sub.connect('inproc://PublisherToProxy')
        self._coverart_sub.setsockopt(zmq.SUBSCRIBE, b'coverart.ready')

        self.display = _create_display()
        self._coverart_cache_manager = _create_coverart_cache_manager()
        self.running = True

        self._pending_status = None
        self._pending_lock = threading.Lock()
        self._update_event = threading.Event()

        self._last_key = None
        self._clear_timer = None
        self._timer_lock = threading.Lock()
        self._last_file_path = None
        self._pending_coverart = None

        self._receiver_thread = threading.Thread(target=self._event_loop, daemon=True, name='DisplayReceiver')
        self._worker_thread = threading.Thread(target=self._worker_loop, daemon=True, name='DisplayWorker')

    def start(self):
        """Start the receiver and worker threads."""
        self._receiver_thread.start()
        self._worker_thread.start()
        logger.info('Display subscriber started')

    def stop(self):
        """Stop the subscriber threads and clear the display."""
        self.running = False
        self._status_sub.close()
        self._coverart_sub.close()
        self._update_event.set()
        self._receiver_thread.join(timeout=2.0)
        self._worker_thread.join(timeout=2.0)
        self._cancel_clear_timer()
        self.display.clear()
        logger.info('Display subscriber stopped')

    def _event_loop(self):
        """
        Receive playerstatus and coverart messages and schedule the latest update.
        """
        poller = zmq.Poller()
        poller.register(self._status_sub, zmq.POLLIN)
        poller.register(self._coverart_sub, zmq.POLLIN)

        while self.running:
            try:
                socks = dict(poller.poll(timeout=500))
            except zmq.ZMQError:
                break

            if not self.running:
                break

            if self._status_sub in socks and socks[self._status_sub] == zmq.POLLIN:
                try:
                    topic, message = self._status_sub.recv_multipart()
                except zmq.ZMQError:
                    break
                try:
                    status = json.loads(message)
                except json.JSONDecodeError as e:
                    logger.error(f'Error decoding playerstatus JSON: {e}')
                    continue

                with self._pending_lock:
                    self._pending_status = status
                self._update_event.set()

            if self._coverart_sub in socks and socks[self._coverart_sub] == zmq.POLLIN:
                try:
                    topic, message = self._coverart_sub.recv_multipart()
                except zmq.ZMQError:
                    break
                try:
                    payload = json.loads(message)
                except json.JSONDecodeError as e:
                    logger.error(f'Error decoding coverart JSON: {e}')
                    continue

                # If the ready cover art belongs to the currently displayed file,
                # trigger a refresh with the new cover art.
                if payload and self._last_file_path:
                    ready_path = payload.get('mp3_file_path', '')
                    expected_path = str(_resolve_music_file(self._last_file_path) or '')
                    logger.debug(f'Coverart ready event: ready_path={ready_path}, expected_path={expected_path}, last_file={self._last_file_path}')
                    if ready_path and expected_path and ready_path == expected_path:
                        self._pending_coverart = payload.get('cache_filename')
                        with self._pending_lock:
                            # Force a re-render by clearing the last key
                            self._last_key = None
                        self._update_event.set()

    def _worker_loop(self):
        """
        Process display updates one at a time, always using the latest pending status.
        """
        while self.running:
            self._update_event.wait()
            if not self.running:
                break

            with self._pending_lock:
                status = self._pending_status
                self._pending_status = None

            self._update_event.clear()

            if status is not None:
                try:
                    self._update_display(status)
                except Exception as e:
                    logger.error(f'Error updating display: {e}')

    def _cancel_clear_timer(self):
        with self._timer_lock:
            if self._clear_timer is not None:
                self._clear_timer.cancel()
                self._clear_timer = None

    def _schedule_clear(self):
        self._cancel_clear_timer()
        with self._timer_lock:
            self._clear_timer = threading.Timer(CLEAR_DELAY_SECONDS, self._do_clear)
            self._clear_timer.start()

    def _do_clear(self):
        with self._timer_lock:
            self._clear_timer = None
        self.display.clear()

    def _update_display(self, status):
        title, artist, state, file_path, repeat_info, album = _format_status(status)

        # Create a key that represents the meaningful displayed content.
        # Include title, artist and repeat_info to catch delayed metadata updates
        # and repeat mode changes. Ignore elapsed/duration changes.
        key = (file_path, state, title, artist, repeat_info, album)

        if key == self._last_key and not self._pending_coverart:
            return
        self._last_key = key

        coverart = self._pending_coverart
        self._pending_coverart = None

        if state == 'play':
            self._cancel_clear_timer()
            self._last_file_path = file_path
            if coverart is None:
                coverart = _get_coverart_path_for_file(file_path, self._coverart_cache_manager)
            coverart_path = _resolve_coverart_path(coverart)
            logger.debug(f'Resolved coverart path: {coverart_path}')
            self.display.show(title, artist, album=album, repeat_info=repeat_info, coverart=coverart_path)
        elif state == 'pause':
            self._cancel_clear_timer()
            self._last_file_path = file_path
            if coverart is None:
                coverart = _get_coverart_path_for_file(file_path, self._coverart_cache_manager)
            coverart_path = _resolve_coverart_path(coverart)
            logger.debug(f'Resolved coverart path: {coverart_path}')
            self.display.show(title, artist, album=album, paused=True, repeat_info=repeat_info, coverart=coverart_path)
        elif state == 'stop':
            self._last_file_path = None
            # Delay clear to avoid flicker during track/folder changes.
            self._schedule_clear()
        else:
            self._last_file_path = None
            self._cancel_clear_timer()
            self.display.clear()


subscriber = None


@plugin.initialize
def initialize():
    global subscriber

    enable = cfg_main.setndefault('display', 'enable', value=False)
    config_file = cfg_display.setndefault('display', 'config_file', value='../../shared/settings/display.yaml')

    if not enable:
        return
    try:
        jukebox.cfghandler.load_yaml(cfg_display, config_file)
    except Exception as e:
        logger.error(f"Disable DISPLAY due to error loading DISPLAY config file. {e.__class__.__name__}: {e}")
        return

    subscriber = DisplaySubscriber()
    subscriber.start()


@plugin.atexit
def atexit(**ignored_kwargs):
    global subscriber
    if subscriber is not None:
        subscriber.stop()
