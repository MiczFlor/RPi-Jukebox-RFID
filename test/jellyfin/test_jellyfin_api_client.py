import json
import threading
import time

import pytest
import requests

from components.jellyfin.jellyfin_api_client import (
    DEFAULT_DEVICE_ID,
    JellyfinApiClient,
    JellyfinAuthError,
    expand_jellyfin_host,
    probe_jellyfin_host,
)
from components.jellyfin.jellyfin_token_store import JellyfinTokenStore

HOST = 'http://jellyfin.local:8096'
USERNAME = 'test-user'
PASSWORD = 'secret-password'
USER_TOKEN = 'user-access-token'
USER_ID = 'user-id'


class FakeResponse:
    def __init__(self, payload=None, status=200, content=None):
        self.payload = payload
        self.status_code = status
        self.ok = 200 <= status < 300
        if content is None:
            content = b'' if payload is None else json.dumps(payload).encode()
        self.content = content
        self.text = self.content.decode()

    def json(self):
        return self.payload

    def raise_for_status(self):
        if not self.ok:
            raise requests.HTTPError(f'HTTP {self.status_code}')


class FakeSession:
    def __init__(self, responses):
        self.responses = list(responses)
        self.calls = []
        self.headers = {}

    def get(self, url, params=None, timeout=None):
        self.calls.append(('GET', url, params, timeout))
        response = self.responses.pop(0)
        if isinstance(response, Exception):
            raise response
        return response

    def post(self, url, json=None, headers=None, timeout=None):
        self.calls.append(('POST', url, json, headers, timeout))
        response = self.responses.pop(0)
        if isinstance(response, Exception):
            raise response
        return response

    def close(self):
        self.calls.append(('CLOSE', None, None, None))


class LoginCountingSession(FakeSession):
    """Answer logins and catalog queries; count the login requests."""

    def __init__(self):
        super().__init__([])
        self.logins = 0
        self._lock = threading.Lock()

    def post(self, url, json=None, headers=None, timeout=None):
        with self._lock:
            self.logins += 1
            self.calls.append(('POST', url, json, timeout))
        # Widen the window in which a second caller could log in as well.
        time.sleep(0.01)
        return FakeResponse(
            {'AccessToken': USER_TOKEN, 'User': {'Id': USER_ID}})

    def get(self, url, params=None, timeout=None):
        with self._lock:
            self.calls.append(('GET', url, params, timeout))
        return FakeResponse({'Items': [{'Id': 'album-1'}]})


class BarrieredExpirySession(FakeSession):
    """Hand the first two GETs a 401 for the same token, then answer."""

    def __init__(self, barrier):
        super().__init__([])
        self.barrier = barrier
        self.logins = 0
        self._lock = threading.Lock()

    def post(self, url, json=None, headers=None, timeout=None):
        with self._lock:
            self.logins += 1
            self.calls.append(('POST', url, json, timeout))
        return FakeResponse(
            {'AccessToken': 'renewed-token', 'User': {'Id': USER_ID}})

    def get(self, url, params=None, timeout=None):
        with self._lock:
            self.calls.append(('GET', url, params, timeout))
            seen = len([call for call in self.calls if call[0] == 'GET'])
        if seen <= 2:
            try:
                self.barrier.wait(timeout=5)
            except threading.BrokenBarrierError:
                pass
            return FakeResponse({}, status=401)
        return FakeResponse({'Items': [{'Id': 'album-1'}]})


@pytest.fixture
def token_store(tmp_path):
    """Return a store that already holds a token for USERNAME."""
    store = JellyfinTokenStore(tmp_path / 'jellyfin_token.json')
    store.save(USER_TOKEN, USER_ID, USERNAME, DEFAULT_DEVICE_ID)
    return store


@pytest.fixture
def make_client(token_store):
    """Return a factory for clients that are authenticated from the store."""
    def factory(session):
        return JellyfinApiClient(HOST, username=USERNAME, password=PASSWORD,
                                 session=session, token_store=token_store)
    return factory


@pytest.fixture
def make_login_client():
    """Return a factory for clients that have to log in first."""
    def factory(session):
        return JellyfinApiClient(HOST, username=USERNAME, password=PASSWORD,
                                 session=session)
    return factory


# ----------------------------------------------------------------------
# Authentication
# ----------------------------------------------------------------------


def test_authenticate_user_success(make_login_client):
    session = FakeSession([
        FakeResponse({'AccessToken': USER_TOKEN, 'User': {'Id': USER_ID}}),
    ])
    client = make_login_client(session)

    assert client.authenticate_user() is True
    method, url, body, headers, _ = session.calls[0]
    assert method == 'POST'
    assert url == f'{HOST}/Users/AuthenticateByName'
    assert body == {'Username': USERNAME, 'Pw': PASSWORD}
    # The identity travels in the session header, not per request.
    assert headers is None
    assert client._access_token == USER_TOKEN
    assert client._user_id == USER_ID
    assert session.headers['Authorization'].startswith('MediaBrowser ')
    assert f'Token="{USER_TOKEN}"' in session.headers['Authorization']


@pytest.mark.parametrize('status', [401, 403])
def test_authenticate_user_rejected(make_login_client, status):
    session = FakeSession([FakeResponse({}, status=status)])
    client = make_login_client(session)

    assert client.authenticate_user() is False
    assert client._access_token is None


def test_authenticate_user_raises_on_transport_error(make_login_client):
    session = FakeSession([requests.ConnectionError('boom')])
    client = make_login_client(session)

    with pytest.raises(requests.RequestException):
        client.authenticate_user()


def test_authenticate_user_error_does_not_leak_password(make_login_client):
    session = FakeSession([requests.ConnectionError('boom')])
    client = make_login_client(session)

    with pytest.raises(requests.RequestException) as error:
        client.authenticate_user()

    assert PASSWORD not in str(error.value)


def test_missing_login_credentials_returns_false():
    client = JellyfinApiClient(HOST, session=FakeSession([]))

    assert client.authenticate_user() is False


def test_ensure_auth_raises_when_credentials_missing():
    client = JellyfinApiClient(HOST, session=FakeSession([]))

    with pytest.raises(JellyfinAuthError):
        client.get_albums()


def test_ensure_auth_raises_when_login_fails(make_login_client):
    session = FakeSession([FakeResponse({}, status=401)])
    client = make_login_client(session)

    with pytest.raises(JellyfinAuthError):
        client.get_albums()


def test_authorization_header_is_the_only_auth_header(make_client):
    session = FakeSession([FakeResponse({'Items': []})])

    make_client(session)

    assert session.headers['Authorization'].startswith('MediaBrowser ')
    assert f'Token="{USER_TOKEN}"' in session.headers['Authorization']
    assert 'X-MediaBrowser-Token' not in session.headers
    assert not [key for key in session.headers if key.startswith('X-Emby')]


def test_auth_header_carries_the_configured_device_id(tmp_path):
    store = JellyfinTokenStore(tmp_path / 'jellyfin_token.json')
    store.save(USER_TOKEN, USER_ID, USERNAME, 'device-42')
    session = FakeSession([])

    JellyfinApiClient(HOST, username=USERNAME, password=PASSWORD,
                      session=session, token_store=store, device_id='device-42')

    assert 'DeviceId="device-42"' in session.headers['Authorization']


def test_token_from_store_is_used_without_login(make_client):
    session = FakeSession([FakeResponse({'Items': [{'Id': 'album-1'}]})])
    client = make_client(session)

    assert client.get_albums() == [{'Id': 'album-1'}]
    assert [call[0] for call in session.calls] == ['GET']


def test_stored_token_for_other_user_is_discarded(tmp_path):
    store = JellyfinTokenStore(tmp_path / 'jellyfin_token.json')
    store.save(USER_TOKEN, USER_ID, 'someone-else', DEFAULT_DEVICE_ID)
    session = FakeSession([
        FakeResponse({'AccessToken': 'fresh-token', 'User': {'Id': USER_ID}}),
        FakeResponse({'Items': [{'Id': 'album-1'}]}),
    ])
    client = JellyfinApiClient(HOST, username=USERNAME, password=PASSWORD,
                               session=session, token_store=store)

    assert client.get_albums() == [{'Id': 'album-1'}]
    assert session.calls[0][0] == 'POST'
    assert client._access_token == 'fresh-token'


def test_stored_token_for_other_device_is_discarded(tmp_path):
    store = JellyfinTokenStore(tmp_path / 'jellyfin_token.json')
    store.save(USER_TOKEN, USER_ID, USERNAME, 'other-device')
    session = FakeSession([
        FakeResponse({'AccessToken': 'fresh-token', 'User': {'Id': USER_ID}}),
        FakeResponse({'Items': [{'Id': 'album-1'}]}),
    ])
    client = JellyfinApiClient(HOST, username=USERNAME, password=PASSWORD,
                               session=session, token_store=store)

    assert client.get_albums() == [{'Id': 'album-1'}]
    assert session.calls[0][0] == 'POST'


def test_token_is_persisted_after_login(tmp_path):
    store = JellyfinTokenStore(tmp_path / 'jellyfin_token.json')
    session = FakeSession([
        FakeResponse({'AccessToken': USER_TOKEN, 'User': {'Id': USER_ID}}),
    ])
    client = JellyfinApiClient(HOST, username=USERNAME, password=PASSWORD,
                               session=session, token_store=store)

    assert client.authenticate_user() is True
    payload = json.loads(store.path.read_text(encoding='utf-8'))
    assert payload['access_token'] == USER_TOKEN
    assert payload['user_id'] == USER_ID
    assert payload['token_username'] == USERNAME
    assert payload['token_device_id'] == DEFAULT_DEVICE_ID


def test_login_survives_unwritable_token_file(tmp_path):
    directory = tmp_path / 'blocked'
    directory.mkdir()
    store = JellyfinTokenStore(directory)
    session = FakeSession([
        FakeResponse({'AccessToken': USER_TOKEN, 'User': {'Id': USER_ID}}),
    ])
    client = JellyfinApiClient(HOST, username=USERNAME, password=PASSWORD,
                               session=session, token_store=store)

    assert client.authenticate_user() is True
    assert client._access_token == USER_TOKEN


def test_login_runs_once_for_concurrent_callers():
    session = LoginCountingSession()
    client = JellyfinApiClient(HOST, username=USERNAME, password=PASSWORD,
                               session=session)
    results = []

    threads = [threading.Thread(target=lambda: results.append(
        client.get_albums())) for _ in range(2)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join(timeout=5)

    assert results == [[{'Id': 'album-1'}], [{'Id': 'album-1'}]]
    assert session.logins == 1


def test_catalog_relogs_in_when_token_expired(token_store):
    session = FakeSession([
        FakeResponse({}, status=401),
        FakeResponse({'AccessToken': 'renewed-token', 'User': {'Id': USER_ID}}),
        FakeResponse({'Items': [{'Id': 'album-1'}]}),
    ])
    client = JellyfinApiClient(HOST, username=USERNAME, password=PASSWORD,
                               session=session, token_store=token_store)

    assert client.get_albums() == [{'Id': 'album-1'}]
    assert client._access_token == 'renewed-token'
    assert token_store.load(USERNAME, DEFAULT_DEVICE_ID) == (
        'renewed-token', USER_ID)


def test_second_401_for_an_old_token_does_not_log_in_again(token_store):
    session = FakeSession([
        FakeResponse({'AccessToken': 'renewed-token', 'User': {'Id': USER_ID}}),
    ])
    client = JellyfinApiClient(HOST, username=USERNAME, password=PASSWORD,
                               session=session, token_store=token_store)

    # Two callers hold a 401 for the same token: the first one logs in, the
    # second one merely retries with the newer token.
    assert client._refresh_auth(USER_TOKEN) is True
    assert client._refresh_auth(USER_TOKEN) is True

    assert [call[0] for call in session.calls] == ['POST']


def test_concurrent_401_refreshes_once(token_store):
    session = BarrieredExpirySession(threading.Barrier(2))
    client = JellyfinApiClient(HOST, username=USERNAME, password=PASSWORD,
                               session=session, token_store=token_store)
    results = []

    threads = [threading.Thread(target=lambda: results.append(
        client.get_albums())) for _ in range(2)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join(timeout=5)

    assert results == [[{'Id': 'album-1'}], [{'Id': 'album-1'}]]
    assert session.logins == 1


def test_coverart_relogs_in_when_token_expired(token_store):
    session = FakeSession([
        FakeResponse({}, status=401),
        FakeResponse({'AccessToken': 'renewed-token', 'User': {'Id': USER_ID}}),
        FakeResponse(content=b'image-bytes'),
    ])
    client = JellyfinApiClient(HOST, username=USERNAME, password=PASSWORD,
                               session=session, token_store=token_store)

    assert client.get_coverart_bytes('track-1') == b'image-bytes'
    assert client._access_token == 'renewed-token'


# ----------------------------------------------------------------------
# Catalog
# ----------------------------------------------------------------------


def test_get_items_in_folder(make_client):
    session = FakeSession([FakeResponse({'Items': [{'Id': 'folder-child'}]})])
    client = make_client(session)

    assert client.get_items_in_folder('folder-1') == [{'Id': 'folder-child'}]
    _, url, params, _ = session.calls[0]
    assert url == f'{HOST}/Items'
    assert params['parentId'] == 'folder-1'
    assert params['Recursive'] == 'false'


def test_get_albums(make_client):
    session = FakeSession([FakeResponse({'Items': [{'Id': 'album-1'}]})])
    client = make_client(session)

    assert client.get_albums() == [{'Id': 'album-1'}]
    _, url, params, _ = session.calls[0]
    assert url == f'{HOST}/Items'
    assert params['includeItemTypes'] == 'MusicAlbum'
    assert params['Recursive'] == 'true'


def test_catalog_payload_flags_on_albums(make_client):
    session = FakeSession([FakeResponse({'Items': []})])
    client = make_client(session)

    client.get_albums()
    _, _, params, _ = session.calls[0]

    assert params['EnableUserData'] == 'false'
    assert params['EnableImageTypes'] == 'Primary'
    assert params['ImageTypeLimit'] == '1'
    assert params['userId'] == USER_ID
    assert 'Fields' not in params


def test_get_albums_optional_pagination_params(make_client):
    session = FakeSession([FakeResponse({'Items': []})])
    client = make_client(session)

    client.get_albums(limit=50, start_index=100)
    _, _, params, _ = session.calls[0]

    assert params['Limit'] == 50
    assert params['StartIndex'] == 100


def test_get_album_children(make_client):
    session = FakeSession([FakeResponse({'Items': [{'Id': 'track-1'}]})])
    client = make_client(session)

    assert client.get_album_children('album-1') == [{'Id': 'track-1'}]
    _, url, params, _ = session.calls[0]
    assert url == f'{HOST}/Items'
    assert params['parentId'] == 'album-1'
    assert params['Recursive'] == 'false'
    assert params['includeItemTypes'] == 'Audio'


def test_catalog_payload_flags_on_album_children(make_client):
    session = FakeSession([FakeResponse({'Items': []})])
    client = make_client(session)

    client.get_album_children('album-1')
    _, _, params, _ = session.calls[0]

    assert params['EnableUserData'] == 'false'
    assert params['EnableImageTypes'] == 'Primary'
    assert params['ImageTypeLimit'] == '1'
    assert params['userId'] == USER_ID
    assert 'Fields' not in params


def test_get_item(make_client):
    session = FakeSession([FakeResponse({'Id': 'track-1', 'Type': 'Audio'})])
    client = make_client(session)

    assert client.get_item('track-1') == {'Id': 'track-1', 'Type': 'Audio'}
    _, url, params, _ = session.calls[0]
    assert url == f'{HOST}/Items/track-1'


def test_get_item_falls_back_to_ids_query(make_client):
    session = FakeSession([
        FakeResponse({}, status=400),
        FakeResponse({'Items': [{'Id': 'track-1', 'Type': 'Audio'}]}),
    ])
    client = make_client(session)

    assert client.get_item('track-1') == {'Id': 'track-1', 'Type': 'Audio'}
    assert session.calls[0][1] == f'{HOST}/Items/track-1'
    fallback_url, fallback_params = session.calls[1][1], session.calls[1][2]
    assert fallback_url == f'{HOST}/Items'
    assert fallback_params['Ids'] == 'track-1'
    assert fallback_params['Recursive'] == 'false'


def test_get_item_fallback_returns_empty_when_missing(make_client):
    session = FakeSession([
        FakeResponse({}, status=400),
        FakeResponse({'Items': []}),
    ])
    client = make_client(session)

    assert client.get_item('missing-1') == {}


def test_get_item_does_not_swallow_auth_error():
    client = JellyfinApiClient(HOST, session=FakeSession([]))

    with pytest.raises(JellyfinAuthError):
        client.get_item('track-1')


def test_search(make_client):
    session = FakeSession([FakeResponse({'SearchHints': [{'Id': 'hit-1'}]})])
    client = make_client(session)

    assert client.search('query') == [{'Id': 'hit-1'}]
    _, url, params, _ = session.calls[0]
    assert url == f'{HOST}/Search/Hints'
    assert params['searchTerm'] == 'query'


def test_request_exception_propagates_from_catalog(make_client):
    session = FakeSession([requests.ConnectionError('offline')])
    client = make_client(session)

    with pytest.raises(requests.RequestException):
        client.get_albums()


# ----------------------------------------------------------------------
# Streaming, cover art, lifecycle
# ----------------------------------------------------------------------


def test_get_stream_url(make_client):
    client = make_client(FakeSession([]))

    url = client.get_stream_url('track-1')

    assert url == (
        f'{HOST}/Audio/track-1/stream?static=true&ApiKey={USER_TOKEN}'
    )
    assert 'api_key=' not in url


def test_get_stream_url_without_credentials_raises():
    client = JellyfinApiClient(HOST, session=FakeSession([]))

    with pytest.raises(JellyfinAuthError):
        client.get_stream_url('track-1')


def test_get_coverart_bytes(make_client):
    session = FakeSession([FakeResponse(content=b'image-bytes')])
    client = make_client(session)

    assert client.get_coverart_bytes('track-1', max_size=300) == b'image-bytes'
    _, url, params, _ = session.calls[0]
    assert url == f'{HOST}/Items/track-1/Images/Primary?maxHeight=300&maxWidth=300'


def test_close_closes_session(make_client):
    session = FakeSession([])
    client = make_client(session)

    client.close()

    assert session.calls[-1][0] == 'CLOSE'


def test_host_trailing_slash_is_stripped(make_client):
    session = FakeSession([])
    client = JellyfinApiClient(f'{HOST}/', username=USERNAME,
                               password=PASSWORD, session=session)

    assert client.host == HOST


def test_host_without_scheme_is_prefixed(make_client):
    session = FakeSession([FakeResponse({'Items': []})])
    client = JellyfinApiClient('192.168.178.26:8096', username=USERNAME,
                               password=PASSWORD, session=session,
                               token_store=make_client(FakeSession([]))
                               ._token_store)

    assert client.host == 'http://192.168.178.26:8096'
    client.get_albums()
    assert session.calls[0][1] == 'http://192.168.178.26:8096/Items'


def test_default_timeout_is_thirty_seconds():
    client = JellyfinApiClient(HOST, session=FakeSession([]))

    assert client.timeout == 30.0


def test_timeout_is_applied_to_requests(token_store):
    session = FakeSession([FakeResponse({'Items': []})])
    client = JellyfinApiClient(HOST, username=USERNAME, password=PASSWORD,
                               session=session, timeout=45.0,
                               token_store=token_store)

    client.get_albums()

    assert session.calls[0][3] == 45.0


# ----------------------------------------------------------------------
# Host expansion and probing
# ----------------------------------------------------------------------


def test_expand_host_bare_address_tries_scheme_and_port_combinations():
    assert expand_jellyfin_host('192.168.1.10') == [
        'http://192.168.1.10:8096',
        'https://192.168.1.10:8920',
        'http://192.168.1.10:8920',
        'https://192.168.1.10:8096',
    ]


def test_expand_host_with_port_only_tries_both_schemes():
    assert expand_jellyfin_host('192.168.1.10:8096') == [
        'http://192.168.1.10:8096',
        'https://192.168.1.10:8096',
    ]


def test_expand_host_custom_port_is_kept():
    assert expand_jellyfin_host('192.168.1.10:1234') == [
        'http://192.168.1.10:1234',
        'https://192.168.1.10:1234',
    ]


def test_expand_host_with_scheme_only_uses_scheme_ports():
    assert expand_jellyfin_host('http://192.168.1.10') == [
        'http://192.168.1.10:8096',
        'http://192.168.1.10:8920',
    ]
    assert expand_jellyfin_host('https://192.168.1.10') == [
        'https://192.168.1.10:8920',
        'https://192.168.1.10:8096',
    ]


def test_expand_host_full_address_is_returned_verbatim():
    assert expand_jellyfin_host('http://192.168.1.10:8096') == [
        'http://192.168.1.10:8096',
    ]


def test_expand_host_strips_trailing_slash_and_keeps_path():
    assert expand_jellyfin_host('192.168.1.10/') == [
        'http://192.168.1.10:8096',
        'https://192.168.1.10:8920',
        'http://192.168.1.10:8920',
        'https://192.168.1.10:8096',
    ]
    assert expand_jellyfin_host('http://host:8096/jellyfin') == [
        'http://host:8096/jellyfin',
    ]


def test_expand_host_ipv6_is_bracketed():
    assert expand_jellyfin_host('::1') == [
        'http://[::1]:8096',
        'https://[::1]:8920',
        'http://[::1]:8920',
        'https://[::1]:8096',
    ]
    assert expand_jellyfin_host('[::1]:8096') == [
        'http://[::1]:8096',
        'https://[::1]:8096',
    ]


@pytest.mark.parametrize('host', ['', '   ', 'http://'])
def test_expand_host_empty_input_returns_no_candidates(host):
    assert expand_jellyfin_host(host) == []


def test_probe_returns_first_candidate_answering_system_info():
    session = FakeSession([
        requests.ConnectionError('refused'),
        FakeResponse({'Version': '12.1.0'}),
    ])

    found = probe_jellyfin_host(
        ['http://host:8096', 'https://host:8920'],
        session=session,
    )

    assert found == 'https://host:8920'
    assert session.calls[0][1] == 'http://host:8096/System/Info/Public'
    assert session.calls[1][1] == 'https://host:8920/System/Info/Public'


def test_probe_ignores_non_jellyfin_responses():
    session = FakeSession([
        FakeResponse({'Server': 'nginx'}),
    ])

    found = probe_jellyfin_host(['http://host:8096'], session=session)

    # The candidate answered but its payload carries no Jellyfin Version,
    # so the probe reports nothing found.
    assert found is None


def test_probe_returns_none_when_all_candidates_fail():
    session = FakeSession([
        requests.ConnectionError('refused'),
        FakeResponse({}, status=404),
    ])

    assert probe_jellyfin_host(
        ['http://host:8096', 'https://host:8920'],
        session=session,
    ) is None
