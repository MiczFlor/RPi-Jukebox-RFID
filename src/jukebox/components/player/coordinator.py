import logging
import threading
from typing import Any, Dict, Optional

import jukebox.plugs as plugs

from .playcontentcallback import PlayCardState, PlayContentCallbacks


logger = logging.getLogger('jb.player')


class PlayerCoordinator:
    """Provider-neutral facade for playback and content backends."""

    def __init__(self, play_card_callbacks: Optional[PlayContentCallbacks] = None):
        self._backends: Dict[str, Any] = {}
        self._active_backend_name: Optional[str] = None
        self._lock = threading.RLock()
        self._play_card_callbacks = play_card_callbacks

    def register_backend(self, name: str, backend: Any, make_active: bool = False) -> None:
        """Register a backend, selecting the first registered backend by default."""
        if not name:
            raise ValueError("Player backend name must not be empty")
        with self._lock:
            if name in self._backends:
                raise ValueError(f"Player backend '{name}' is already registered")
            self._backends[name] = backend
            if self._active_backend_name is None or make_active:
                self._select_backend(name)

    def _get_backend(self, name: str) -> Any:
        try:
            return self._backends[name]
        except KeyError:
            available = ', '.join(self._backends) or 'none'
            raise KeyError(
                f"Unknown player backend '{name}'. Available backends: {available}"
            ) from None

    def _get_active_backend(self) -> Any:
        if self._active_backend_name is None:
            raise RuntimeError("No player backend is registered")
        return self._get_backend(self._active_backend_name)

    def _select_backend(self, name: str) -> Any:
        backend = self._get_backend(name)
        if self._active_backend_name == name:
            return backend
        if self._active_backend_name is not None:
            self._call_backend(self._get_active_backend(), 'stop')
        self._active_backend_name = name
        logger.info(f"Selected player backend '{name}'")
        return backend

    def _call_backend(self, backend: Any, method: str, *args, **kwargs):
        func = getattr(backend, method, None)
        if not callable(func):
            backend_name = backend.__class__.__name__
            raise NotImplementedError(
                f"Player backend '{backend_name}' does not support '{method}'"
            )
        return func(*args, **kwargs)

    def _call_active(self, method: str, *args, **kwargs):
        with self._lock:
            return self._call_backend(self._get_active_backend(), method, *args, **kwargs)

    @plugs.tag
    def list_backends(self):
        with self._lock:
            return list(self._backends)

    @plugs.tag
    def get_active_backend(self):
        with self._lock:
            return self._active_backend_name

    @plugs.tag
    def select_backend(self, name: str):
        """Stop the current backend and select another registered backend."""
        with self._lock:
            self._select_backend(name)
            return name

    @plugs.tag
    def get_player_type_and_version(self):
        return self._call_active('get_player_type_and_version')

    @plugs.tag
    def update(self):
        return self._call_active('update')

    @plugs.tag
    def update_wait(self):
        return self._call_active('update_wait')

    @plugs.tag
    def play(self):
        return self._call_active('play')

    @plugs.tag
    def stop(self):
        return self._call_active('stop')

    @plugs.tag
    def pause(self, state: int = 1):
        return self._call_active('pause', state)

    @plugs.tag
    def prev(self):
        return self._call_active('prev')

    @plugs.tag
    def next(self):
        return self._call_active('next')

    @plugs.tag
    def seek(self, new_time):
        return self._call_active('seek', new_time)

    @plugs.tag
    def rewind(self):
        return self._call_active('rewind')

    @plugs.tag
    def replay(self):
        return self._call_active('replay')

    @plugs.tag
    def toggle(self):
        return self._call_active('toggle')

    @plugs.tag
    def replay_if_stopped(self):
        return self._call_active('replay_if_stopped')

    @plugs.tag
    def shuffle(self, option='toggle'):
        return self._call_active('shuffle', option)

    @plugs.tag
    def repeat(self, option='toggle'):
        return self._call_active('repeat', option)

    @plugs.tag
    def get_current_song(self, param):
        return self._call_active('get_current_song', param)

    @plugs.tag
    def map_filename_to_playlist_pos(self, filename):
        return self._call_active('map_filename_to_playlist_pos', filename)

    @plugs.tag
    def remove(self):
        return self._call_active('remove')

    @plugs.tag
    def move(self):
        return self._call_active('move')

    @plugs.tag
    def play_single(self, song_url):
        return self._call_active('play_single', song_url)

    @plugs.tag
    def resume(self):
        return self._call_active('resume')

    @plugs.tag
    def play_card(self, folder: str, recursive: bool = False):
        with self._lock:
            backend = self._get_active_backend()
            is_second_swipe = self._call_backend(backend, 'is_second_swipe', folder)
            if is_second_swipe:
                if self._play_card_callbacks is not None:
                    self._play_card_callbacks.run_callbacks(folder, PlayCardState.secondSwipe)
                return self._call_backend(backend, 'play_second_swipe')

            if self._play_card_callbacks is not None:
                self._play_card_callbacks.run_callbacks(folder, PlayCardState.firstSwipe)
            return self._call_backend(backend, 'play_folder', folder, recursive)

    @plugs.tag
    def get_single_coverart(self, song_url):
        return self._call_active('get_single_coverart', song_url)

    @plugs.tag
    def get_album_coverart(self, albumartist: str, album: str):
        return self._call_active('get_album_coverart', albumartist, album)

    @plugs.tag
    def flush_coverart_cache(self):
        return self._call_active('flush_coverart_cache')

    @plugs.tag
    def get_folder_content(self, folder: str):
        return self._call_active('get_folder_content', folder)

    @plugs.tag
    def play_folder(self, folder: str, recursive: bool = False) -> None:
        return self._call_active('play_folder', folder, recursive)

    @plugs.tag
    def play_album(self, albumartist: str, album: str):
        return self._call_active('play_album', albumartist, album)

    @plugs.tag
    def queue_load(self, folder):
        return self._call_active('queue_load', folder)

    @plugs.tag
    def playerstatus(self):
        return self._call_active('playerstatus')

    @plugs.tag
    def playlistinfo(self):
        return self._call_active('playlistinfo')

    @plugs.tag
    def list_all_dirs(self):
        return self._call_active('list_all_dirs')

    @plugs.tag
    def list_albums(self):
        return self._call_active('list_albums')

    @plugs.tag
    def list_songs_by_artist_and_album(self, albumartist, album):
        return self._call_active('list_songs_by_artist_and_album', albumartist, album)

    @plugs.tag
    def get_song_by_url(self, song_url):
        return self._call_active('get_song_by_url', song_url)

    def get_volume(self):
        return self._call_active('get_volume')

    def set_volume(self, volume):
        return self._call_active('set_volume', volume)

    def exit(self):
        with self._lock:
            return [
                self._call_backend(backend, 'exit')
                for backend in reversed(list(self._backends.values()))
            ]
