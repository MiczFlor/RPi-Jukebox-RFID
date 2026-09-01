import json

import pytest
import requests

from components.jellyfin.jellyfin_api_client import (
    JellyfinApiClient,
    expand_jellyfin_host,
    probe_jellyfin_host,
)

HOST = 'http://jellyfin.local:8096'
API_KEY = 'test-api-key'


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


def make_client(session):
    return JellyfinApiClient(HOST, API_KEY, session=session)


def test_authenticate_success():
    session = FakeSession([FakeResponse({})])
    client = make_client(session)

    assert client.authenticate() is True
    method, url, params, timeout = session.calls[0]
    assert method == 'GET'
    assert url == f'{HOST}/Users/Me'
    assert timeout is not None


@pytest.mark.parametrize('status', [401, 403])
def test_authenticate_rejected_key(status):
    session = FakeSession([FakeResponse({}, status=status)])
    client = make_client(session)

    assert client.authenticate() is False


def test_authenticate_connection_error_raises():
    session = FakeSession([requests.ConnectionError('boom')])
    client = make_client(session)

    with pytest.raises(requests.RequestException):
        client.authenticate()


def test_authenticate_error_does_not_leak_api_key():
    session = FakeSession([requests.ConnectionError('boom')])
    client = make_client(session)

    with pytest.raises(requests.RequestException) as error:
        client.authenticate()

    assert API_KEY not in str(error.value)


def test_get_items_in_folder():
    session = FakeSession([FakeResponse({'Items': [{'Id': 'folder-child'}]})])
    client = make_client(session)

    assert client.get_items_in_folder('folder-1') == [{'Id': 'folder-child'}]
    _, url, params, _ = session.calls[0]
    assert url == f'{HOST}/Items'
    assert params['parentId'] == 'folder-1'
    assert params['Recursive'] == 'false'


def test_get_albums():
    session = FakeSession([FakeResponse({'Items': [{'Id': 'album-1'}]})])
    client = make_client(session)

    assert client.get_albums() == [{'Id': 'album-1'}]
    _, url, params, _ = session.calls[0]
    assert url == f'{HOST}/Items'
    assert params['includeItemTypes'] == 'MusicAlbum'
    assert params['Recursive'] == 'true'


def test_catalog_payload_flags_on_albums():
    session = FakeSession([FakeResponse({'Items': []})])
    client = make_client(session)

    client.get_albums()
    _, _, params, _ = session.calls[0]

    assert params['EnableUserData'] == 'false'
    assert params['EnableImageTypes'] == 'Primary'
    assert params['ImageTypeLimit'] == '1'
    assert 'Fields' not in params


def test_get_albums_optional_pagination_params():
    session = FakeSession([FakeResponse({'Items': []})])
    client = make_client(session)

    client.get_albums(limit=50, start_index=100)
    _, _, params, _ = session.calls[0]

    assert params['Limit'] == 50
    assert params['StartIndex'] == 100


def test_get_album_children():
    session = FakeSession([FakeResponse({'Items': [{'Id': 'track-1'}]})])
    client = make_client(session)

    assert client.get_album_children('album-1') == [{'Id': 'track-1'}]
    _, url, params, _ = session.calls[0]
    assert url == f'{HOST}/Items'
    assert params['parentId'] == 'album-1'
    assert params['Recursive'] == 'false'
    assert params['includeItemTypes'] == 'Audio'


def test_catalog_payload_flags_on_album_children():
    session = FakeSession([FakeResponse({'Items': []})])
    client = make_client(session)

    client.get_album_children('album-1')
    _, _, params, _ = session.calls[0]

    assert params['EnableUserData'] == 'false'
    assert params['EnableImageTypes'] == 'Primary'
    assert params['ImageTypeLimit'] == '1'
    assert 'Fields' not in params


def test_get_item():
    session = FakeSession([FakeResponse({'Id': 'track-1', 'Type': 'Audio'})])
    client = make_client(session)

    assert client.get_item('track-1') == {'Id': 'track-1', 'Type': 'Audio'}
    _, url, params, _ = session.calls[0]
    assert url == f'{HOST}/Items/track-1'


def test_search():
    session = FakeSession([FakeResponse({'SearchHints': [{'Id': 'hit-1'}]})])
    client = make_client(session)

    assert client.search('query') == [{'Id': 'hit-1'}]
    _, url, params, _ = session.calls[0]
    assert url == f'{HOST}/Search/Hints'
    assert params['searchTerm'] == 'query'


def test_get_stream_url():
    client = make_client(FakeSession([]))

    assert client.get_stream_url('track-1') == (
        f'{HOST}/Audio/track-1/stream?static=true&api_key={API_KEY}'
    )


def test_get_coverart_bytes():
    session = FakeSession([FakeResponse(content=b'image-bytes')])
    client = make_client(session)

    assert client.get_coverart_bytes('track-1', max_size=300) == b'image-bytes'
    _, url, params, _ = session.calls[0]
    assert url == f'{HOST}/Items/track-1/Images/Primary?maxHeight=300&maxWidth=300'


def test_request_exception_propagates_from_catalog():
    session = FakeSession([requests.ConnectionError('offline')])
    client = make_client(session)

    with pytest.raises(requests.RequestException):
        client.get_albums()


def test_close_closes_session():
    session = FakeSession([])
    client = make_client(session)

    client.close()

    assert session.calls[-1][0] == 'CLOSE'


def test_auth_header_sent_on_every_request():
    session = FakeSession([FakeResponse({'Items': []})])
    make_client(session)

    assert session.headers['X-Emby-Token'] == API_KEY
    assert session.headers['X-Emby-Client'] == 'Phoniebox'
    assert session.headers['X-Emby-Device-Id'] == 'phoniebox'


def test_host_trailing_slash_is_stripped():
    session = FakeSession([FakeResponse({'Items': []})])
    client = JellyfinApiClient(f'{HOST}/', API_KEY, session=session)

    assert client.host == HOST


def test_host_without_scheme_is_prefixed():
    session = FakeSession([FakeResponse({'Items': []})])
    client = JellyfinApiClient('192.168.178.26:8096', API_KEY, session=session)

    assert client.host == 'http://192.168.178.26:8096'
    client.get_albums()
    assert session.calls[0][1] == 'http://192.168.178.26:8096/Items'


def test_default_timeout_is_thirty_seconds():
    client = JellyfinApiClient(HOST, API_KEY, session=FakeSession([]))

    assert client.timeout == 30.0


def test_timeout_is_applied_to_requests():
    session = FakeSession([FakeResponse({})])
    client = JellyfinApiClient(HOST, API_KEY, session=session, timeout=45.0)

    client.authenticate()

    assert session.calls[0][3] == 45.0


def test_authenticate_falls_back_to_system_info():
    session = FakeSession([
        FakeResponse({}, status=400),
        FakeResponse({}, status=200),
    ])
    client = make_client(session)

    assert client.authenticate() is True
    assert session.calls[0][1] == f'{HOST}/Users/Me'
    assert session.calls[1][1] == f'{HOST}/System/Info'


def test_authenticate_fallback_rejected_key():
    session = FakeSession([
        FakeResponse({}, status=400),
        FakeResponse({}, status=401),
    ])
    client = make_client(session)

    assert client.authenticate() is False


def test_get_item_falls_back_to_ids_query():
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


def test_get_item_fallback_returns_empty_when_missing():
    session = FakeSession([
        FakeResponse({}, status=400),
        FakeResponse({'Items': []}),
    ])
    client = make_client(session)

    assert client.get_item('missing-1') == {}


USERNAME = 'test-user'
PASSWORD = 'secret-password'
USER_TOKEN = 'user-access-token'


def make_login_client(session):
    return JellyfinApiClient(
        HOST, username=USERNAME, password=PASSWORD, session=session)


def test_authenticate_user_success():
    session = FakeSession([FakeResponse({'AccessToken': USER_TOKEN})])
    client = make_login_client(session)

    assert client.authenticate_user() is True
    method, url, body, headers, timeout = session.calls[0]
    assert method == 'POST'
    assert url == f'{HOST}/Users/AuthenticateByName'
    assert body == {'Username': USERNAME, 'Pw': PASSWORD}
    assert 'X-Emby-Authorization' in headers
    assert client.api_key == USER_TOKEN
    assert session.headers['X-Emby-Token'] == USER_TOKEN


@pytest.mark.parametrize('status', [401, 403])
def test_authenticate_user_rejected(status):
    session = FakeSession([FakeResponse({}, status=status)])
    client = make_login_client(session)

    assert client.authenticate_user() is False
    assert client.api_key == ''


def test_authenticate_user_raises_on_transport_error():
    session = FakeSession([requests.ConnectionError('boom')])
    client = make_login_client(session)

    with pytest.raises(requests.RequestException):
        client.authenticate_user()


def test_authenticate_user_error_does_not_leak_password():
    session = FakeSession([requests.ConnectionError('boom')])
    client = make_login_client(session)

    with pytest.raises(requests.RequestException) as error:
        client.authenticate_user()

    assert PASSWORD not in str(error.value)


def test_authenticate_prefers_login_when_configured():
    session = FakeSession([FakeResponse({'AccessToken': USER_TOKEN})])
    client = make_login_client(session)

    assert client.authenticate() is True
    assert session.calls[0][1] == f'{HOST}/Users/AuthenticateByName'


def test_catalog_authenticates_lazily_with_login():
    session = FakeSession([
        FakeResponse({'AccessToken': USER_TOKEN}),
        FakeResponse({'Items': [{'Id': 'album-1'}]}),
    ])
    client = make_login_client(session)

    assert client.get_albums() == [{'Id': 'album-1'}]
    assert session.calls[0][1] == f'{HOST}/Users/AuthenticateByName'
    assert session.calls[1][1] == f'{HOST}/Items'


def test_stream_url_uses_user_token_after_login():
    session = FakeSession([FakeResponse({'AccessToken': USER_TOKEN})])
    client = make_login_client(session)
    client.authenticate_user()

    stream_url = client.get_stream_url('track-1')

    assert USER_TOKEN in stream_url
    assert API_KEY not in stream_url


def test_catalog_relogs_in_when_token_expired():
    session = FakeSession([
        FakeResponse({'AccessToken': USER_TOKEN}),
        FakeResponse({}, status=401),
        FakeResponse({'AccessToken': 'renewed-token'}),
        FakeResponse({'Items': [{'Id': 'album-1'}]}),
    ])
    client = make_login_client(session)

    assert client.get_albums() == [{'Id': 'album-1'}]
    assert client.api_key == 'renewed-token'


def test_missing_login_credentials_returns_false():
    client = JellyfinApiClient(HOST, session=FakeSession([]))

    assert client.authenticate_user() is False


def test_coverart_relogs_in_when_token_expired():
    session = FakeSession([
        FakeResponse({'AccessToken': USER_TOKEN}),
        FakeResponse({}, status=401),
        FakeResponse({'AccessToken': 'renewed-token'}),
        FakeResponse(content=b'image-bytes'),
    ])
    client = make_login_client(session)

    assert client.get_coverart_bytes('track-1') == b'image-bytes'
    assert client.api_key == 'renewed-token'


# ---------------------------------------------------------------------------
# Host expansion and probing
# ---------------------------------------------------------------------------


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
        FakeResponse({'Version': '10.9.0'}),
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
