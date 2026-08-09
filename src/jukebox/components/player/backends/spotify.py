"""Spotify playback backend controlled through the official Web API."""

import logging
import threading
import time

import jukebox.multitimer as multitimer
import jukebox.publishing as publishing

from ..spotify import SpotifyCatalog, SpotifyError, _first_image


logger = logging.getLogger('jb.player.spotify')
TRANSFER_RETRY_DELAY = 0.5


class SpotifyPlayer:
    """Control a configured librespot Spotify Connect device."""

    def __init__(self, service, poll_interval=1.0):
        self.service = service
        self.api = service.api
        self.catalog = service.catalog
        self.device_name = service.device_name
        self._active = False
        self._device_id = None
        self._status = self._empty_status()
        self._lock = threading.RLock()
        self._status_timer = multitimer.GenericEndlessTimerClass(
            'spotify.timer_status',
            poll_interval,
            self._poll_status,
        )
        self._status_timer.start()

    def set_active(self, active):
        with self._lock:
            self._active = active
        if active:
            self._poll_status()

    def get_player_type_and_version(self):
        return 'Spotify Web API with librespot'

    def play(self):
        self._start_playback()
        self._poll_status()

    def stop(self):
        if not self.service.oauth.connected:
            return
        if not self._device_id:
            return
        try:
            self.api.put('/me/player/pause', params=self._device_params())
        except SpotifyError as error:
            if error.status not in (404, 403):
                raise
        self._status = self._empty_status()
        self._publish_status()

    def pause(self, state=1):
        if int(state):
            self.api.put('/me/player/pause', params=self._device_params())
        else:
            self.play()
        self._poll_status()

    def prev(self):
        self.api.post('/me/player/previous', params=self._device_params())
        self._poll_status()

    def next(self):
        self.api.post('/me/player/next', params=self._device_params())
        self._poll_status()

    def seek(self, new_time):
        self.api.put(
            '/me/player/seek',
            params={**self._device_params(), 'position_ms': int(float(new_time) * 1000)},
        )
        self._poll_status()

    def rewind(self):
        return self.seek(0)

    def replay(self):
        return self.seek(0)

    def toggle(self):
        if self._status.get('state') == 'play':
            return self.pause(1)
        return self.play()

    def replay_if_stopped(self):
        if self._status.get('state') == 'stop':
            return self.replay()
        return self.play()

    def shuffle(self, option='toggle'):
        current = self._status.get('random') == '1'
        enabled = not current if option == 'toggle' else option == 'enable'
        self.api.put(
            '/me/player/shuffle',
            params={**self._device_params(), 'state': str(enabled).lower()},
        )
        self._poll_status()

    def repeat(self, option='toggle'):
        current = self._status.get('repeat') == '1'
        single = self._status.get('single') == '1'
        if option == 'toggle':
            state = 'context' if not current and not single else ('track' if current else 'off')
        elif option in ('toggle_repeat', 'enable_repeat'):
            state = 'off' if current else 'context'
        elif option in ('toggle_repeat_single', 'enable_repeat_single'):
            state = 'off' if single else 'track'
        else:
            state = 'off'
        self.api.put(
            '/me/player/repeat',
            params={**self._device_params(), 'state': state},
        )
        self._poll_status()

    def get_current_song(self, param):
        return self._status.get(param) if param else self._status

    def play_single(self, song_url):
        self._start_playback({'uris': [song_url]})
        self._poll_status()

    def play_album(self, albumartist, album, content_uri=None):
        if not content_uri:
            raise SpotifyError(
                'Spotify album and playlist cards require a content_uri.',
                code='missing_spotify_uri',
            )
        if content_uri == SpotifyCatalog.SAVED_TRACKS_URI:
            track_uris = self.catalog.saved_track_uris()
            if not track_uris:
                raise SpotifyError('The Spotify Liked Songs collection is empty.')
            body = {'uris': track_uris}
        elif content_uri.startswith('spotify:track:'):
            body = {'uris': [content_uri]}
        else:
            body = {'context_uri': content_uri}
        self._start_playback(body)
        self._poll_status()

    def get_single_coverart(self, song_url):
        return self.catalog.get_song(song_url).get('cover_url')

    def get_album_coverart(self, albumartist, album, content_uri=None):
        songs = self.catalog.list_songs(
            content_uri,
            albumartist=albumartist,
            album=album,
        )
        return songs[0].get('cover_url') if songs else None

    def playerstatus(self):
        return self._status

    def playlistinfo(self):
        return [self._status] if self._status.get('songid') else []

    def list_albums(self):
        return self.catalog.list_albums()

    def library_source(self):
        return {
            'id': 'spotify',
            'label': 'Spotify',
            'views': [
                {
                    'id': 'albums',
                    'label': 'Albums',
                    'kind': 'items',
                    'content_types': ['album'],
                },
                {
                    'id': 'playlists',
                    'label': 'Playlists',
                    'kind': 'items',
                    'content_types': ['playlist'],
                },
                {
                    'id': 'tracks',
                    'label': 'Tracks',
                    'kind': 'items',
                    'content_types': ['track', 'collection'],
                },
            ],
        }

    def list_library_items(self, content_types=None):
        return self.catalog.list_library_items(content_types)

    def list_songs_by_artist_and_album(self, albumartist, album, content_uri=None):
        if not content_uri:
            raise SpotifyError(
                'Spotify catalog requests require a content_uri.',
                code='missing_spotify_uri',
            )
        return self.catalog.list_songs(
            content_uri,
            albumartist=albumartist,
            album=album,
        )

    def get_song_by_url(self, song_url):
        return [self.catalog.get_song(song_url)]

    def exit(self):
        self._status_timer.close()
        return self._status_timer.timer_thread

    def _start_playback(self, body=None):
        device_id, transferred = self._ensure_device()
        try:
            self.api.put(
                '/me/player/play',
                params={'device_id': device_id},
                json_body=body,
            )
        except SpotifyError as error:
            is_transfer_race = (
                transferred
                and error.status == 403
                and 'restriction violated' in str(error).lower()
            )
            if not is_transfer_race:
                raise
            logger.info(
                "Retrying playback after activating Spotify device '%s'",
                self.device_name,
            )
            time.sleep(TRANSFER_RETRY_DELAY)
            self.api.put(
                '/me/player/play',
                params={'device_id': device_id},
                json_body=body,
            )

    def _ensure_device(self):
        devices = self.api.get('/me/player/devices').get('devices', [])
        matching = next(
            (device for device in devices if device.get('name') == self.device_name),
            None,
        )
        if matching is None:
            raise SpotifyError(
                f"Spotify Connect device '{self.device_name}' is not available. "
                'Start librespot and connect to it once from a Spotify app.',
                code='spotify_device_unavailable',
            )
        self._device_id = matching['id']
        transferred = not matching.get('is_active')
        if transferred:
            self.api.put(
                '/me/player',
                json_body={'device_ids': [self._device_id], 'play': False},
            )
        return self._device_id, transferred

    def _device_params(self):
        return {'device_id': self._device_id} if self._device_id else None

    def _poll_status(self):
        with self._lock:
            if not self._active or not self.service.oauth.connected:
                return
        try:
            playback = self.api.get('/me/player')
            device = (playback or {}).get('device') or {}
            if device.get('name') == self.device_name:
                self._device_id = device.get('id')
                self._status = self._normalize_status(playback)
            else:
                self._status = self._empty_status()
            self._publish_status()
        except SpotifyError as error:
            logger.warning('Could not update Spotify playback status: %s', error)

    def _publish_status(self):
        with self._lock:
            if self._active:
                publishing.get_publisher().send('playerstatus', self._status)

    @staticmethod
    def _empty_status():
        return {
            'state': 'stop',
            'elapsed': '0.0',
            'duration': '0.0',
            'random': '0',
            'repeat': '0',
            'single': '0',
            'provider': 'spotify',
        }

    @classmethod
    def _normalize_status(cls, playback):
        if not playback or not playback.get('item'):
            return cls._empty_status()
        track = playback['item']
        album = track.get('album') or {}
        repeat_state = playback.get('repeat_state')
        return {
            'state': 'play' if playback.get('is_playing') else 'pause',
            'songid': track.get('uri') or track.get('id'),
            'song': str(track.get('track_number') or ''),
            'title': track.get('name') or '',
            'artist': ', '.join(
                artist.get('name', '')
                for artist in track.get('artists', [])
                if artist.get('name')
            ),
            'album': album.get('name') or '',
            'file': track.get('uri'),
            'elapsed': str(float(playback.get('progress_ms') or 0) / 1000),
            'duration': str(float(track.get('duration_ms') or 0) / 1000),
            'random': '1' if playback.get('shuffle_state') else '0',
            'repeat': '1' if repeat_state == 'context' else '0',
            'single': '1' if repeat_state == 'track' else '0',
            'provider': 'spotify',
            'cover_url': _first_image(album.get('images')),
        }
