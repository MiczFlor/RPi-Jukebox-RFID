import json
import stat
from types import SimpleNamespace
from unittest.mock import Mock
from urllib.parse import parse_qs, urlparse

import pytest

from components.player.backends import spotify as spotify_backend
from components.player.backends.spotify import SpotifyPlayer
from components.player.coordinator import PlayerCoordinator
from components.player.spotify import (
    SpotifyCatalog,
    SpotifyError,
    SpotifyLibrary,
    SpotifyLibraryStore,
    SpotifyOAuth,
    SpotifyTokenStore,
    SpotifyWebApiClient,
)


class FakeResponse:
    def __init__(self, payload=None, status=200):
        self.payload = payload
        self.status_code = status
        self.ok = 200 <= status < 300
        self.content = b'' if payload is None else json.dumps(payload).encode()
        self.text = self.content.decode()

    def json(self):
        return self.payload


class NonJsonResponse(FakeResponse):
    def __init__(self, body, status=200):
        super().__init__(status=status)
        self.content = body.encode()
        self.text = body

    def json(self):
        raise ValueError('not JSON')


class FakeSession:
    def __init__(self, responses):
        self.responses = list(responses)
        self.calls = []

    def post(self, url, **kwargs):
        self.calls.append(('POST', url, kwargs))
        return self.responses.pop(0)

    def request(self, method, url, **kwargs):
        self.calls.append((method, url, kwargs))
        return self.responses.pop(0)


def test_pkce_authorization_stores_and_refreshes_tokens(tmp_path):
    session = FakeSession([
        FakeResponse({
            'access_token': 'initial',
            'refresh_token': 'refresh',
            'expires_in': 60,
        }),
        FakeResponse({
            'access_token': 'refreshed',
            'expires_in': 3600,
        }),
    ])
    token_path = tmp_path / 'spotify.json'
    now = [1000]
    oauth = SpotifyOAuth(
        'client-id',
        'https://box.example/api/v1/spotify/oauth/callback',
        SpotifyTokenStore(token_path),
        session=session,
        clock=lambda: now[0],
    )

    authorization_url = oauth.authorization_url()
    query = parse_qs(urlparse(authorization_url).query)
    assert query['client_id'] == ['client-id']
    assert query['code_challenge_method'] == ['S256']
    assert 'user-library-read' in query['scope'][0]

    oauth.complete('authorization-code', query['state'][0])

    stored = json.loads(token_path.read_text())
    assert stored['refresh_token'] == 'refresh'
    assert stat.S_IMODE(token_path.stat().st_mode) == 0o600
    assert oauth.access_token() == 'initial'

    now[0] = 1031
    assert oauth.access_token() == 'refreshed'
    refresh_call = session.calls[-1]
    assert refresh_call[2]['data']['grant_type'] == 'refresh_token'
    assert json.loads(token_path.read_text())['refresh_token'] == 'refresh'


def test_web_api_refreshes_once_after_an_unauthorized_response(tmp_path):
    token_store = SpotifyTokenStore(tmp_path / 'tokens.json')
    token_store.save({
        'access_token': 'expired-at-server',
        'refresh_token': 'refresh',
        'expires_at': 9999,
    })
    oauth_session = FakeSession([
        FakeResponse({'access_token': 'new', 'expires_in': 3600}),
    ])
    oauth = SpotifyOAuth(
        'client',
        'https://box.example/callback',
        token_store,
        session=oauth_session,
        clock=lambda: 100,
    )
    api_session = FakeSession([
        FakeResponse({'error': {'message': 'expired'}}, status=401),
        FakeResponse({'devices': []}),
    ])
    api = SpotifyWebApiClient(oauth, session=api_session)

    assert api.get('/me/player/devices') == {'devices': []}
    assert len(api_session.calls) == 2
    assert api_session.calls[-1][2]['headers']['Authorization'] == 'Bearer new'


def test_web_api_accepts_non_json_success_for_player_control():
    oauth = SimpleNamespace(access_token=lambda **kwargs: 'token')
    session = FakeSession([NonJsonResponse('command accepted')])
    api = SpotifyWebApiClient(oauth, session=session)

    assert api.put('/me/player/pause') is None


def test_web_api_preserves_non_json_error_message():
    oauth = SimpleNamespace(access_token=lambda **kwargs: 'token')
    session = FakeSession([NonJsonResponse('service unavailable', status=503)])
    api = SpotifyWebApiClient(oauth, session=session)

    with pytest.raises(SpotifyError, match='service unavailable') as error:
        api.get('/me/player')

    assert error.value.status == 503


class FakeCatalogApi:
    def get(self, path, params=None):
        if path == '/me/tracks':
            return {'total': 1}
        if path == '/albums/album-id':
            return {
                'name': 'Saved Album',
                'images': [{'url': 'https://images/album.jpg'}],
            }
        raise AssertionError(path)

    def paginate(self, path, params=None, item_transform=lambda value: value):
        values = {
            '/me/albums': [{
                'album': {
                    'name': 'Saved Album',
                    'uri': 'spotify:album:album-id',
                    'artists': [{'name': 'Artist'}],
                    'images': [{'url': 'https://images/album.jpg'}],
                },
            }],
            '/me/playlists': [{
                'name': 'Stories',
                'uri': 'spotify:playlist:playlist-id',
                'owner': {'display_name': 'Parent'},
                'images': [{'url': 'https://images/playlist.jpg'}],
            }],
            '/albums/album-id/tracks': [{
                'name': 'Chapter One',
                'uri': 'spotify:track:track-id',
                'artists': [{'name': 'Reader'}],
                'duration_ms': 61000,
                'track_number': 1,
            }],
        }[path]
        return [item_transform(value) for value in values]


def test_catalog_combines_saved_albums_playlists_and_tracks():
    catalog = SpotifyCatalog(FakeCatalogApi())

    entries = catalog.list_albums()

    assert [entry['content_type'] for entry in entries] == [
        'album',
        'playlist',
        'collection',
    ]
    assert all(entry['provider'] == 'spotify' for entry in entries)

    songs = catalog.list_songs('spotify:album:album-id')
    assert songs == [{
        'album': 'Saved Album',
        'artist': 'Reader',
        'duration': 61.0,
        'file': 'spotify:track:track-id',
        'provider': 'spotify',
        'title': 'Chapter One',
        'track': '1',
        'cover_url': 'https://images/album.jpg',
    }]


class FakeCuratedApi:
    def get(self, path, params=None):
        values = {
            '/albums/album-id': {
                'name': 'Bedtime Album',
                'uri': 'spotify:album:album-id',
                'artists': [{'name': 'Storyteller'}],
                'images': [{'url': 'https://images/album.jpg'}],
            },
            '/playlists/playlist-id': {
                'name': 'Quiet Time',
                'uri': 'spotify:playlist:playlist-id',
                'owner': {'display_name': 'Parent'},
                'images': [{'url': 'https://images/playlist.jpg'}],
            },
            '/tracks/track-id': {
                'name': 'One Story',
                'uri': 'spotify:track:track-id',
                'artists': [{'name': 'Reader'}],
                'duration_ms': 90000,
                'track_number': 3,
                'album': {
                    'name': 'Story Collection',
                    'images': [{'url': 'https://images/track.jpg'}],
                },
            },
        }
        return values[path]

    def paginate(self, path, params=None, item_transform=lambda value: value):
        raise AssertionError(f'Curated mode must not read account library: {path}')


def test_curated_library_persists_mode_and_normalized_metadata(tmp_path):
    path = tmp_path / 'spotify_library.json'
    library = SpotifyLibrary(FakeCuratedApi(), SpotifyLibraryStore(path))

    playlist = library.add(
        'https://open.spotify.com/playlist/playlist-id?si=shared-value'
    )
    track = library.add('spotify:track:track-id')
    library.set_mode('curated')

    assert playlist == {
        'albumartist': 'Parent',
        'album': 'Quiet Time',
        'provider': 'spotify',
        'content_uri': 'spotify:playlist:playlist-id',
        'cover_url': 'https://images/playlist.jpg',
        'content_type': 'playlist',
    }
    assert track['content_type'] == 'track'
    assert stat.S_IMODE(path.stat().st_mode) == 0o600
    assert SpotifyLibraryStore(path).state() == library.status()

    library.set_mode('account')
    assert len(library.status()['items']) == 2
    library.set_mode('curated')
    library.remove('https://open.spotify.com/playlist/playlist-id')
    assert [item['content_uri'] for item in library.status()['items']] == [
        'spotify:track:track-id',
    ]
    library.add('spotify:album:album-id')
    with pytest.raises(SpotifyError):
        library.remove_many([
            'spotify:track:track-id',
            'spotify:playlist:missing',
        ])
    assert len(library.status()['items']) == 2
    library.remove_many([
        'spotify:track:track-id',
        'spotify:album:album-id',
    ])
    assert library.status()['items'] == []


def test_curated_catalog_filters_items_and_opens_single_tracks(tmp_path):
    api = FakeCuratedApi()
    library = SpotifyLibrary(api, SpotifyLibraryStore(tmp_path / 'library.json'))
    library.add('spotify:album:album-id')
    library.add('spotify:track:track-id')
    library.set_mode('curated')
    catalog = SpotifyCatalog(api, library)

    assert [item['content_type'] for item in catalog.list_library_items(['track'])] == [
        'track',
    ]
    assert catalog.list_songs('spotify:track:track-id') == [{
        'album': 'Story Collection',
        'artist': 'Reader',
        'duration': 90.0,
        'file': 'spotify:track:track-id',
        'provider': 'spotify',
        'title': 'One Story',
        'track': '3',
        'cover_url': 'https://images/track.jpg',
    }]


@pytest.mark.parametrize(
    'reference',
    [
        'https://example.com/playlist/playlist-id',
        'https://open.spotify.com/artist/artist-id',
        'spotify:show:show-id',
        '',
    ],
)
def test_curated_library_rejects_unsupported_references(tmp_path, reference):
    library = SpotifyLibrary(
        FakeCuratedApi(),
        SpotifyLibraryStore(tmp_path / 'library.json'),
    )

    with pytest.raises(SpotifyError):
        library.add(reference)


class FakeTimer:
    def __init__(self, name, interval, callback):
        self.callback = callback
        self.timer_thread = None

    def start(self):
        pass

    def close(self):
        pass


class FakePlaybackApi:
    def __init__(self, *, active=False, play_errors=None):
        self.calls = []
        self.active = active
        self.play_errors = list(play_errors or [])

    def get(self, path, params=None):
        self.calls.append(('GET', path, params, None))
        if path == '/me/player/devices':
            return {'devices': [{
                'id': 'device-id',
                'name': 'Phoniebox',
                'is_active': self.active,
            }]}
        if path == '/me/player':
            return None
        raise AssertionError(path)

    def put(self, path, params=None, json_body=None):
        self.calls.append(('PUT', path, params, json_body))
        if path == '/me/player/play' and self.play_errors:
            raise self.play_errors.pop(0)

    def post(self, path, params=None, json_body=None):
        self.calls.append(('POST', path, params, json_body))


def test_player_describes_spotify_library_views():
    player = SpotifyPlayer.__new__(SpotifyPlayer)

    assert player.library_source() == {
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


def test_coordinator_infers_spotify_backend_from_content_uri():
    local = SimpleNamespace(
        play_single=Mock(),
        set_active=Mock(),
        stop=Mock(),
    )
    spotify = SimpleNamespace(
        play_single=Mock(),
        set_active=Mock(),
        stop=Mock(),
    )
    coordinator = PlayerCoordinator()
    coordinator.register_backend('mpd', local)
    coordinator.register_backend('spotify', spotify)

    coordinator.play_single('spotify:track:track-id')

    spotify.play_single.assert_called_once_with('spotify:track:track-id')
    local.play_single.assert_not_called()


def test_player_transfers_to_librespot_before_starting_context(monkeypatch):
    monkeypatch.setattr(
        spotify_backend.multitimer,
        'GenericEndlessTimerClass',
        FakeTimer,
    )
    api = FakePlaybackApi()
    service = SimpleNamespace(
        api=api,
        catalog=SimpleNamespace(),
        device_name='Phoniebox',
        oauth=SimpleNamespace(connected=True),
    )
    player = SpotifyPlayer(service)
    player._active = True

    player.play_album('Artist', 'Album', 'spotify:album:album-id')

    assert api.calls[:3] == [
        ('GET', '/me/player/devices', None, None),
        ('PUT', '/me/player', None, {
            'device_ids': ['device-id'],
            'play': False,
        }),
        ('PUT', '/me/player/play', {'device_id': 'device-id'}, {
            'context_uri': 'spotify:album:album-id',
        }),
    ]


def test_player_starts_curated_track_as_single_uri(monkeypatch):
    monkeypatch.setattr(
        spotify_backend.multitimer,
        'GenericEndlessTimerClass',
        FakeTimer,
    )
    api = FakePlaybackApi()
    service = SimpleNamespace(
        api=api,
        catalog=SimpleNamespace(),
        device_name='Phoniebox',
        oauth=SimpleNamespace(connected=True),
    )
    player = SpotifyPlayer(service)
    player._active = True

    player.play_album('Reader', 'One Story', 'spotify:track:track-id')

    assert api.calls[2] == (
        'PUT',
        '/me/player/play',
        {'device_id': 'device-id'},
        {'uris': ['spotify:track:track-id']},
    )


def test_player_retries_restriction_after_device_transfer(monkeypatch):
    monkeypatch.setattr(
        spotify_backend.multitimer,
        'GenericEndlessTimerClass',
        FakeTimer,
    )
    sleep = Mock()
    monkeypatch.setattr(spotify_backend.time, 'sleep', sleep)
    api = FakePlaybackApi(play_errors=[
        SpotifyError(
            'Player command failed: Restriction violated',
            status=403,
        ),
    ])
    service = SimpleNamespace(
        api=api,
        catalog=SimpleNamespace(),
        device_name='Phoniebox',
        oauth=SimpleNamespace(connected=True),
    )
    player = SpotifyPlayer(service)
    player._active = True

    player.play_album('Artist', 'Album', 'spotify:album:album-id')

    play_calls = [call for call in api.calls if call[1] == '/me/player/play']
    assert len(play_calls) == 2
    assert play_calls[0] == play_calls[1]
    sleep.assert_called_once_with(spotify_backend.TRANSFER_RETRY_DELAY)


def test_player_does_not_retry_restriction_on_active_device(monkeypatch):
    monkeypatch.setattr(
        spotify_backend.multitimer,
        'GenericEndlessTimerClass',
        FakeTimer,
    )
    sleep = Mock()
    monkeypatch.setattr(spotify_backend.time, 'sleep', sleep)
    api = FakePlaybackApi(
        active=True,
        play_errors=[
            SpotifyError(
                'Player command failed: Restriction violated',
                status=403,
            ),
        ],
    )
    service = SimpleNamespace(
        api=api,
        catalog=SimpleNamespace(),
        device_name='Phoniebox',
        oauth=SimpleNamespace(connected=True),
    )
    player = SpotifyPlayer(service)
    player._active = True

    with pytest.raises(SpotifyError, match='Restriction violated'):
        player.play_album('Artist', 'Album', 'spotify:album:album-id')

    sleep.assert_not_called()


def test_player_status_matches_existing_mpd_webapp_contract():
    status = SpotifyPlayer._normalize_status({
        'is_playing': True,
        'progress_ms': 12000,
        'shuffle_state': True,
        'repeat_state': 'track',
        'item': {
            'uri': 'spotify:track:track-id',
            'name': 'Chapter One',
            'duration_ms': 61000,
            'track_number': 1,
            'artists': [{'name': 'Reader'}],
            'album': {
                'name': 'Stories',
                'images': [{'url': 'https://images/cover.jpg'}],
            },
        },
    })

    assert status['state'] == 'play'
    assert status['songid'] == 'spotify:track:track-id'
    assert status['elapsed'] == '12.0'
    assert status['duration'] == '61.0'
    assert status['random'] == '1'
    assert status['repeat'] == '0'
    assert status['single'] == '1'
    assert status['provider'] == 'spotify'
