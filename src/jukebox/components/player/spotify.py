"""Spotify Web API authentication, catalog access, and playback requests."""

import base64
import hashlib
import json
import logging
import os
import secrets
import tempfile
import threading
import time
from pathlib import Path
from urllib.parse import urlencode, urlparse

import requests


logger = logging.getLogger('jb.player.spotify')

SPOTIFY_ACCOUNTS_URL = 'https://accounts.spotify.com'
SPOTIFY_API_URL = 'https://api.spotify.com/v1'
SPOTIFY_SCOPES = (
    'playlist-read-collaborative',
    'playlist-read-private',
    'user-library-read',
    'user-modify-playback-state',
    'user-read-currently-playing',
    'user-read-playback-state',
)


class SpotifyError(RuntimeError):
    """An expected Spotify configuration, authentication, or API failure."""

    def __init__(self, message, *, status=None, code='spotify_error'):
        super().__init__(message)
        self.status = status
        self.code = code


class SpotifyJsonStore:
    """Persist Spotify state atomically with owner-only permissions."""

    def __init__(self, path):
        self.path = Path(path).expanduser()
        self._lock = threading.RLock()

    def load(self):
        with self._lock:
            try:
                with self.path.open(encoding='utf-8') as stream:
                    value = json.load(stream)
            except FileNotFoundError:
                return None
            except (OSError, json.JSONDecodeError) as error:
                logger.warning("Could not read Spotify state '%s': %s", self.path, error)
                return None
            return value if isinstance(value, dict) else None

    def save(self, tokens):
        with self._lock:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            file_descriptor, temporary_name = tempfile.mkstemp(
                prefix=f'.{self.path.name}.',
                dir=self.path.parent,
            )
            try:
                os.fchmod(file_descriptor, 0o600)
                with os.fdopen(file_descriptor, 'w', encoding='utf-8') as stream:
                    json.dump(tokens, stream)
                    stream.flush()
                    os.fsync(stream.fileno())
                os.replace(temporary_name, self.path)
                os.chmod(self.path, 0o600)
            except Exception:
                try:
                    os.close(file_descriptor)
                except OSError:
                    pass
                try:
                    os.unlink(temporary_name)
                except FileNotFoundError:
                    pass
                raise

    def clear(self):
        with self._lock:
            try:
                self.path.unlink()
            except FileNotFoundError:
                pass


class SpotifyTokenStore(SpotifyJsonStore):
    """Persist OAuth tokens atomically with owner-only permissions."""


class SpotifyLibraryStore(SpotifyJsonStore):
    """Persist the selected library mode and curated Spotify items."""

    MODES = ('account', 'curated')

    def state(self):
        value = self.load() or {}
        mode = value.get('mode', 'account')
        items = value.get('items', [])
        return {
            'mode': mode if mode in self.MODES else 'account',
            'items': [
                item for item in items
                if isinstance(item, dict) and item.get('content_uri')
            ] if isinstance(items, list) else [],
        }

    def set_mode(self, mode):
        if mode not in self.MODES:
            raise SpotifyError(
                f"Unsupported Spotify library mode '{mode}'.",
                status=400,
                code='invalid_spotify_library_mode',
            )
        with self._lock:
            state = self.state()
            state['mode'] = mode
            self.save(state)
            return state

    def upsert(self, item):
        with self._lock:
            state = self.state()
            state['items'] = [
                entry for entry in state['items']
                if entry.get('content_uri') != item['content_uri']
            ]
            state['items'].append(item)
            self.save(state)
            return state

    def remove(self, content_uri):
        return self.remove_many([content_uri])

    def remove_many(self, content_uris):
        with self._lock:
            state = self.state()
            requested = set(content_uris)
            existing = {
                item.get('content_uri')
                for item in state['items']
            }
            if not requested or not requested.issubset(existing):
                raise SpotifyError(
                    'One or more Spotify items are not in the curated library.',
                    status=404,
                    code='spotify_library_item_not_found',
                )
            remaining = [
                item for item in state['items']
                if item.get('content_uri') not in requested
            ]
            state['items'] = remaining
            self.save(state)
            return state


class SpotifyOAuth:
    """Authorization Code with PKCE lifecycle for a user-owned Spotify app."""

    def __init__(
            self,
            client_id,
            redirect_uri,
            token_store,
            *,
            session=None,
            clock=time.time):
        self.client_id = client_id.strip() if isinstance(client_id, str) else ''
        self.redirect_uri = redirect_uri.strip() if isinstance(redirect_uri, str) else ''
        self.token_store = token_store
        self.session = session or requests.Session()
        self.clock = clock
        self._tokens = token_store.load()
        self._pending = {}
        self._lock = threading.RLock()

    @property
    def configured(self):
        return bool(self.client_id and self.redirect_uri)

    @property
    def connected(self):
        with self._lock:
            return bool(self._tokens and self._tokens.get('refresh_token'))

    def status(self):
        return {
            'configured': self.configured,
            'connected': self.connected,
            'redirect_uri': self.redirect_uri or None,
        }

    def authorization_url(self):
        if not self.configured:
            raise SpotifyError(
                'Spotify client_id and redirect_uri must be configured first.',
                code='spotify_not_configured',
            )

        verifier = secrets.token_urlsafe(64)
        challenge = base64.urlsafe_b64encode(
            hashlib.sha256(verifier.encode('ascii')).digest()
        ).rstrip(b'=').decode('ascii')
        state = secrets.token_urlsafe(32)
        now = self.clock()
        with self._lock:
            self._pending = {
                key: value
                for key, value in self._pending.items()
                if now - value['created_at'] < 600
            }
            self._pending[state] = {
                'created_at': now,
                'verifier': verifier,
            }

        query = urlencode({
            'client_id': self.client_id,
            'response_type': 'code',
            'redirect_uri': self.redirect_uri,
            'scope': ' '.join(SPOTIFY_SCOPES),
            'code_challenge_method': 'S256',
            'code_challenge': challenge,
            'state': state,
        })
        return f'{SPOTIFY_ACCOUNTS_URL}/authorize?{query}'

    def complete(self, code, state):
        with self._lock:
            pending = self._pending.pop(state, None)
        if pending is None or self.clock() - pending['created_at'] >= 600:
            raise SpotifyError(
                'The Spotify authorization request has expired or is invalid.',
                code='invalid_oauth_state',
            )
        tokens = self._token_request({
            'client_id': self.client_id,
            'grant_type': 'authorization_code',
            'code': code,
            'redirect_uri': self.redirect_uri,
            'code_verifier': pending['verifier'],
        })
        self._store_tokens(tokens)

    def disconnect(self):
        with self._lock:
            self._tokens = None
            self._pending.clear()
            self.token_store.clear()

    def access_token(self, *, force_refresh=False):
        with self._lock:
            if not self._tokens:
                raise SpotifyError(
                    'Connect a Spotify account before using this feature.',
                    status=401,
                    code='spotify_not_connected',
                )
            expires_at = float(self._tokens.get('expires_at', 0))
            if not force_refresh and self._tokens.get('access_token') and expires_at > self.clock():
                return self._tokens['access_token']

            refresh_token = self._tokens.get('refresh_token')
            if not refresh_token:
                raise SpotifyError(
                    'Spotify authorization has expired. Connect the account again.',
                    status=401,
                    code='spotify_not_connected',
                )
            tokens = self._token_request({
                'client_id': self.client_id,
                'grant_type': 'refresh_token',
                'refresh_token': refresh_token,
            })
            tokens.setdefault('refresh_token', refresh_token)
            self._store_tokens(tokens)
            return self._tokens['access_token']

    def _token_request(self, data):
        try:
            response = self.session.post(
                f'{SPOTIFY_ACCOUNTS_URL}/api/token',
                data=data,
                timeout=15,
            )
        except requests.RequestException as error:
            raise SpotifyError(f'Could not reach Spotify Accounts: {error}') from error
        if not response.ok:
            message = _spotify_error_message(response)
            raise SpotifyError(
                f'Spotify authorization failed: {message}',
                status=response.status_code,
                code='spotify_authorization_failed',
            )
        try:
            return response.json()
        except ValueError as error:
            raise SpotifyError('Spotify returned an invalid token response.') from error

    def _store_tokens(self, tokens):
        stored = dict(tokens)
        stored['expires_at'] = self.clock() + int(stored.get('expires_in', 3600)) - 30
        with self._lock:
            self.token_store.save(stored)
            self._tokens = stored


class SpotifyWebApiClient:
    """Small authenticated client for the Spotify Web API."""

    def __init__(self, oauth, *, session=None, api_url=SPOTIFY_API_URL):
        self.oauth = oauth
        self.session = session or requests.Session()
        self.api_url = api_url.rstrip('/')

    def request(self, method, path, *, params=None, json_body=None, retry=True):
        url = path if path.startswith('http') else f'{self.api_url}/{path.lstrip("/")}'
        headers = {'Authorization': f'Bearer {self.oauth.access_token()}'}
        try:
            response = self.session.request(
                method,
                url,
                params=params,
                json=json_body,
                headers=headers,
                timeout=15,
            )
        except requests.RequestException as error:
            raise SpotifyError(f'Could not reach Spotify: {error}') from error

        if response.status_code == 401 and retry:
            self.oauth.access_token(force_refresh=True)
            return self.request(
                method,
                path,
                params=params,
                json_body=json_body,
                retry=False,
            )
        if not response.ok:
            raise SpotifyError(
                _spotify_error_message(response),
                status=response.status_code,
                code='spotify_api_error',
            )
        if response.status_code == 204 or not response.content:
            return None
        try:
            return response.json()
        except ValueError as error:
            if method.upper() != 'GET':
                return None
            raise SpotifyError('Spotify returned an invalid API response.') from error

    def get(self, path, **kwargs):
        return self.request('GET', path, **kwargs)

    def put(self, path, **kwargs):
        return self.request('PUT', path, **kwargs)

    def post(self, path, **kwargs):
        return self.request('POST', path, **kwargs)

    def paginate(self, path, *, params=None, item_transform=lambda value: value):
        result = []
        page = self.get(path, params=params)
        while page:
            result.extend(
                item_transform(item)
                for item in page.get('items', [])
                if item is not None
            )
            next_page = page.get('next')
            page = self.get(next_page) if next_page else None
        return result


class SpotifyCatalog:
    """Expose the user's saved Spotify content in the player catalog shape."""

    SAVED_TRACKS_URI = 'spotify:collection:tracks'

    def __init__(self, api, library=None):
        self.api = api
        self.library = library

    def list_albums(self):
        return self.list_library_items()

    def list_library_items(self, content_types=None):
        selected_types = None if content_types is None else set(content_types)
        library_state = self.library.status() if self.library is not None else None
        if library_state is not None and library_state['mode'] == 'curated':
            return [
                item for item in library_state['items']
                if selected_types is None or item.get('content_type') in selected_types
            ]

        result = []
        if selected_types is None or 'album' in selected_types:
            albums = self.api.paginate(
                '/me/albums',
                params={'limit': 50},
                item_transform=lambda item: item.get('album'),
            )
            result.extend(
                self._album_entry(album)
                for album in albums
                if album and album.get('uri')
            )
        if selected_types is None or 'playlist' in selected_types:
            playlists = self.api.paginate('/me/playlists', params={'limit': 50})
            result.extend(
                self._playlist_entry(playlist)
                for playlist in playlists
                if playlist and playlist.get('uri')
            )
        if selected_types is None or 'collection' in selected_types:
            saved_tracks = self.api.get('/me/tracks', params={'limit': 1})
            if saved_tracks and saved_tracks.get('total', 0):
                result.append({
                    'albumartist': 'Spotify',
                    'album': 'Liked Songs',
                    'provider': 'spotify',
                    'content_uri': self.SAVED_TRACKS_URI,
                    'cover_url': None,
                    'content_type': 'collection',
                })
        return result

    def list_songs(self, content_uri, *, albumartist=None, album=None):
        uri_type, spotify_id = _parse_spotify_uri(content_uri)
        if uri_type == 'album':
            metadata = self.api.get(f'/albums/{spotify_id}')
            tracks = self.api.paginate(
                f'/albums/{spotify_id}/tracks',
                params={'limit': 50},
            )
            return [
                self._track_entry(
                    track,
                    album_name=metadata.get('name'),
                    cover_url=_first_image(metadata.get('images')),
                )
                for track in tracks
            ]
        if uri_type == 'playlist':
            items = self.api.paginate(
                f'/playlists/{spotify_id}/items',
                params={'limit': 50, 'additional_types': 'track'},
            )
            return [
                self._track_entry(_playlist_item_track(item))
                for item in items
                if _playlist_item_track(item)
            ]
        if content_uri == self.SAVED_TRACKS_URI:
            items = self.api.paginate('/me/tracks', params={'limit': 50})
            return [
                self._track_entry(item.get('track'))
                for item in items
                if item.get('track')
            ]
        if uri_type == 'track':
            return [self.get_song(content_uri)]
        raise SpotifyError(
            f"Unsupported Spotify library URI '{content_uri}'.",
            code='unsupported_spotify_uri',
        )

    def get_song(self, song_uri):
        uri_type, spotify_id = _parse_spotify_uri(song_uri)
        if uri_type != 'track':
            raise SpotifyError(
                f"Expected a Spotify track URI, got '{song_uri}'.",
                code='unsupported_spotify_uri',
            )
        return self._track_entry(self.api.get(f'/tracks/{spotify_id}'))

    def saved_track_uris(self, limit=100):
        items = self.api.paginate('/me/tracks', params={'limit': 50})
        return [
            item['track']['uri']
            for item in items[:limit]
            if item.get('track', {}).get('uri')
        ]

    @staticmethod
    def _album_entry(album):
        return {
            'albumartist': _artist_names(album.get('artists')),
            'album': album.get('name') or 'Unknown album',
            'provider': 'spotify',
            'content_uri': album.get('uri'),
            'cover_url': _first_image(album.get('images')),
            'content_type': 'album',
        }

    @staticmethod
    def _playlist_entry(playlist):
        owner = playlist.get('owner') or {}
        owner_name = owner.get('display_name') or owner.get('id') or 'Spotify'
        return {
            'albumartist': owner_name,
            'album': playlist.get('name') or 'Unknown playlist',
            'provider': 'spotify',
            'content_uri': playlist.get('uri'),
            'cover_url': _first_image(playlist.get('images')),
            'content_type': 'playlist',
        }

    @staticmethod
    def _track_entry(track, *, album_name=None, cover_url=None):
        album = track.get('album') or {}
        duration = float(track.get('duration_ms', 0)) / 1000
        return {
            'album': album_name or album.get('name') or '',
            'artist': _artist_names(track.get('artists')),
            'duration': duration,
            'file': track.get('uri'),
            'provider': 'spotify',
            'title': track.get('name') or 'Unknown title',
            'track': str(track.get('track_number') or ''),
            'cover_url': cover_url or _first_image(album.get('images')),
        }


class SpotifyLibrary:
    """Manage account and explicitly curated Spotify library modes."""

    SUPPORTED_TYPES = ('album', 'playlist', 'track')

    def __init__(self, api, store):
        self.api = api
        self.store = store

    def status(self):
        return self.store.state()

    def set_mode(self, mode):
        return self.store.set_mode(mode)

    def add(self, reference):
        content_type, spotify_id, content_uri = _normalize_spotify_reference(reference)
        if content_type == 'album':
            item = SpotifyCatalog._album_entry(
                self.api.get(f'/albums/{spotify_id}')
            )
        elif content_type == 'playlist':
            item = SpotifyCatalog._playlist_entry(
                self.api.get(f'/playlists/{spotify_id}')
            )
        else:
            item = self._track_library_entry(
                self.api.get(f'/tracks/{spotify_id}')
            )
        item['content_uri'] = content_uri
        self.store.upsert(item)
        return item

    def remove(self, reference):
        _, _, content_uri = _normalize_spotify_reference(reference)
        return self.store.remove(content_uri)

    def remove_many(self, references):
        if not isinstance(references, list):
            raise SpotifyError(
                'Spotify library item URIs must be a list.',
                status=400,
                code='invalid_spotify_reference',
            )
        content_uris = [
            _normalize_spotify_reference(reference)[2]
            for reference in references
        ]
        return self.store.remove_many(content_uris)

    @staticmethod
    def _track_library_entry(track):
        album = track.get('album') or {}
        return {
            'albumartist': _artist_names(track.get('artists')) or 'Spotify',
            'album': track.get('name') or 'Unknown title',
            'provider': 'spotify',
            'content_uri': track.get('uri'),
            'cover_url': _first_image(album.get('images')),
            'content_type': 'track',
        }


class SpotifyService:
    """Shared authentication, API, and catalog services."""

    def __init__(self, oauth, api, catalog, library, device_name):
        self.oauth = oauth
        self.api = api
        self.catalog = catalog
        self.library = library
        self.device_name = device_name

    def status(self):
        status = self.oauth.status()
        status['device_name'] = self.device_name
        status['enabled'] = getattr(self, 'enabled', False)
        return status


def create_spotify_service(
        client_id,
        redirect_uri,
        token_file,
        device_name,
        library_file=None,
        *,
        session=None):
    token_store = SpotifyTokenStore(token_file)
    oauth = SpotifyOAuth(client_id, redirect_uri, token_store, session=session)
    api = SpotifyWebApiClient(oauth, session=session)
    if library_file is None:
        library_file = Path(token_file).with_name('spotify_library.json')
    library = SpotifyLibrary(api, SpotifyLibraryStore(library_file))
    return SpotifyService(
        oauth,
        api,
        SpotifyCatalog(api, library),
        library,
        device_name,
    )


def _spotify_error_message(response):
    try:
        payload = response.json()
    except ValueError:
        return response.text or f'Spotify request failed with status {response.status_code}.'
    error = payload.get('error', payload)
    if isinstance(error, dict):
        return error.get('message') or error.get('error_description') or str(error)
    return str(error)


def _artist_names(artists):
    return ', '.join(
        artist.get('name', '')
        for artist in (artists or [])
        if artist.get('name')
    )


def _first_image(images):
    return images[0].get('url') if images else None


def _playlist_item_track(item):
    return item.get('item') or item.get('track')


def _parse_spotify_uri(uri):
    if not isinstance(uri, str):
        raise SpotifyError('Spotify content URI must be a string.', code='unsupported_spotify_uri')
    parts = uri.split(':')
    if len(parts) != 3 or parts[0] != 'spotify' or not parts[2]:
        raise SpotifyError(
            f"Invalid Spotify URI '{uri}'.",
            code='unsupported_spotify_uri',
        )
    return parts[1], parts[2]


def _normalize_spotify_reference(reference):
    if not isinstance(reference, str) or not reference.strip():
        raise SpotifyError(
            'Provide a Spotify album, playlist, or track link.',
            status=400,
            code='invalid_spotify_reference',
        )

    reference = reference.strip()
    if reference.startswith('spotify:'):
        content_type, spotify_id = _parse_spotify_uri(reference)
    else:
        parsed = urlparse(reference)
        if parsed.scheme not in ('http', 'https') or parsed.hostname != 'open.spotify.com':
            raise SpotifyError(
                'Use an open.spotify.com link or Spotify URI.',
                status=400,
                code='invalid_spotify_reference',
            )
        parts = [part for part in parsed.path.split('/') if part]
        if len(parts) == 3 and parts[0].startswith('intl-'):
            parts = parts[1:]
        if len(parts) != 2:
            raise SpotifyError(
                'The Spotify link must point to an album, playlist, or track.',
                status=400,
                code='invalid_spotify_reference',
            )
        content_type, spotify_id = parts

    if content_type not in SpotifyLibrary.SUPPORTED_TYPES or not spotify_id:
        raise SpotifyError(
            'Only Spotify album, playlist, and track links are supported.',
            status=400,
            code='unsupported_spotify_resource',
        )
    return content_type, spotify_id, f'spotify:{content_type}:{spotify_id}'
