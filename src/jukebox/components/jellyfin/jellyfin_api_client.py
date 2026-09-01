"""HTTP client for the Jellyfin REST API.

The client is a pure HTTP wrapper: authenticated catalog queries, stream URL
generation and cover-art downloads. It holds no player state and never logs
the API key or the user credentials.

Authentication supports either an API key or a username/password login. A
login token is bound to the user's library permissions, so a restricted
user only ever sees the content that user is allowed to access.
"""

import logging
from typing import Optional
from urllib.parse import urlunsplit

import requests


logger = logging.getLogger('jb.player.jellyfin')

#: Default request timeout in seconds for all Jellyfin API calls.
DEFAULT_TIMEOUT = 30.0

#: Client identification used for the username/password login request.
AUTH_HEADER = (
    'MediaBrowser Client="Phoniebox", Device="Phoniebox", '
    'DeviceId="phoniebox", Version="3.7.0"'
)

#: Standard Jellyfin ports probed when an address carries no explicit port,
#: mirroring the Jellyfin Android app (8096 = HTTP, 8920 = HTTPS).
JELLYFIN_DEFAULT_PORTS = (8096, 8920)

#: (scheme, port) pairs tried for an incomplete address, most likely first:
#: a server is usually plain HTTP on 8096, HTTPS on 8920 or a cross combo.
JELLYFIN_ADDRESS_COMBINATIONS = (
    ('http', 8096),
    ('https', 8920),
    ('http', 8920),
    ('https', 8096),
)


def _parse_port(value):
    """Return ``value`` as a valid port number, or ``None`` when invalid."""
    try:
        port = int(value)
    except (TypeError, ValueError):
        return None
    return port if 0 < port < 65536 else None


def _split_netloc(netloc):
    """Return ``(netloc, port)``, splitting off an explicit port.

    Handles plain ``host:port`` and bracketed IPv6 ``[addr]:port``. A bare
    IPv6 literal (e.g. ``::1``) is wrapped in brackets so the result can be
    used in a URL.
    """
    if netloc.startswith('['):
        addr = netloc[1:]
        if ']:' in addr:
            addr, _, port_str = addr.partition(']:')
            return f'[{addr}]', _parse_port(port_str)
        return f'[{addr}]', None
    if netloc.count(':') == 1:
        addr, _, port_str = netloc.partition(':')
        parsed = _parse_port(port_str)
        if parsed is not None:
            return addr, parsed
    if ':' in netloc:
        return f'[{netloc}]', None
    return netloc, None


def expand_jellyfin_host(host):
    """Expand a possibly incomplete server address into probe candidates.

    Mirrors the Jellyfin Android app: an address without a scheme is tried
    over both ``http`` and ``https``, an address without a port with the
    standard Jellyfin ports 8096 and 8920. An explicitly given scheme or
    port narrows the candidate list. Returns the candidate URLs (most
    likely first) without duplicates, or an empty list for empty input.
    """
    host = (host or '').strip()
    if not host:
        return []

    scheme = None
    netloc = host
    path = ''
    if '://' in host:
        scheme, _, netloc = host.partition('://')
        scheme = scheme.lower()
    netloc = netloc.rstrip('/')
    if '/' in netloc:
        netloc, _, path = netloc.partition('/')
        path = f'/{path}'

    # Split off an explicit port and bracket bare IPv6 literals.
    netloc, port = _split_netloc(netloc)
    if not netloc:
        return []

    if port is not None:
        schemes = (scheme,) if scheme else ('http', 'https')
        pairs = [(candidate_scheme, port)
                 for candidate_scheme in schemes]
    else:
        pairs = JELLYFIN_ADDRESS_COMBINATIONS
        if scheme:
            pairs = [pair for pair in pairs if pair[0] == scheme]

    candidates = []
    for candidate_scheme, candidate_port in pairs:
        candidate = urlunsplit((
            candidate_scheme, f'{netloc}:{candidate_port}', path, '', ''))
        if candidate not in candidates:
            candidates.append(candidate)
    return candidates


def probe_jellyfin_host(candidates, timeout=3.0, session=None):
    """Return the first candidate URL that answers as a Jellyfin server.

    Each candidate is queried at its public ``/System/Info/Public`` endpoint
    (no authentication required); a JSON payload carrying a ``Version``
    field marks a reachable Jellyfin server. Returns ``None`` when no
    candidate responds. When ``session`` is omitted a short-lived session
    is created and closed again.
    """
    owns_session = session is None
    session = session if session is not None else requests.Session()
    try:
        for candidate in candidates:
            try:
                response = session.get(
                    f'{candidate}/System/Info/Public', timeout=timeout)
            except requests.RequestException:
                continue
            if not response.ok:
                continue
            try:
                info = response.json()
            except ValueError:
                continue
            if isinstance(info, dict) and 'Version' in info:
                return candidate
    finally:
        if owns_session:
            session.close()
    return None


class JellyfinApiClient:
    """Small authenticated client for the Jellyfin REST API (10.8+).

    :param host: Base URL of the Jellyfin server (e.g. ``http://jellyfin.local:8096``).
    :param api_key: Jellyfin API key (``X-Emby-Token``).
    :param username: Optional user name for login-based authentication.
    :param password: Password belonging to ``username``.
    """

    _DEFAULT_HEADERS = {
        'X-Emby-Client': 'Phoniebox',
        'X-Emby-Device-Id': 'phoniebox',
        'X-Emby-Device-Name': 'Phoniebox',
        'Content-Type': 'application/json',
    }

    def __init__(
            self,
            host: str,
            api_key: str = '',
            username: str = '',
            password: str = '',
            *,
            session: Optional[requests.Session] = None,
            timeout: float = DEFAULT_TIMEOUT):
        host = (host or '').strip()
        # A scheme-less host (e.g. "192.168.178.26:8096") is treated as plain
        # HTTP so that requests can build a valid URL.
        if host and '://' not in host:
            host = f'http://{host}'
        self.host = host.rstrip('/')
        self.api_key = api_key or ''
        self.username = username or ''
        self.password = password or ''
        self.timeout = timeout
        self._session = session if session is not None else requests.Session()
        self._session.headers.update(self._DEFAULT_HEADERS)
        if self.api_key:
            self._session.headers['X-Emby-Token'] = self.api_key

    # ------------------------------------------------------------------
    # Authentication
    # ------------------------------------------------------------------

    def authenticate_user(self, username=None, password=None) -> bool:
        """Log in with a Jellyfin user and store the resulting access token.

        The token is scoped to the user's library permissions, so subsequent
        catalog queries only return content that user may access. Returns
        ``False`` when the server rejects the credentials (HTTP 401/403).
        Network/transport failures are raised as ``requests.RequestException``.
        Credentials are never logged.
        """
        username = self.username if username is None else username
        password = self.password if password is None else password
        if not username or not password:
            logger.error('Jellyfin login requires both username and password')
            return False
        response = self._session.post(
            f'{self.host}/Users/AuthenticateByName',
            json={'Username': username, 'Pw': password},
            headers={'X-Emby-Authorization': AUTH_HEADER},
            timeout=self.timeout,
        )
        if response.status_code in (401, 403):
            logger.error(
                'Jellyfin rejected the username/password (HTTP %s)',
                response.status_code)
            return False
        response.raise_for_status()
        token = (response.json().get('AccessToken') or '').strip()
        if not token:
            logger.error('Jellyfin login response contained no access token')
            return False
        self.api_key = token
        self._session.headers['X-Emby-Token'] = token
        logger.info('Jellyfin user logged in')
        return True

    def _ensure_token(self):
        """Log in lazily when login credentials are configured."""
        if not self.api_key and (self.username or self.password):
            if not self.authenticate_user():
                raise requests.HTTPError('Jellyfin login failed')

    def authenticate(self) -> bool:
        """Validate the credentials against the Jellyfin server.

        With ``username``/``password`` configured, this performs the login;
        otherwise the API key is validated. Returns ``True`` when the
        credentials are accepted and ``False`` when the server rejects them
        (HTTP 401/403). Network/transport failures are raised as
        ``requests.RequestException`` so callers can distinguish invalid
        credentials from an unreachable server.

        Some servers reject the authenticated ``/Users/Me`` endpoint with a
        non-401/403 status (e.g. HTTP 400/404 on an incompatible API
        version). As a pragmatic fallback the public ``/System/Info``
        endpoint is then consulted: it answers regardless of the key, so
        ``False`` is only returned when it also answers 401/403.
        """
        if self.username or self.password:
            return self.authenticate_user()
        response = self._session.get(f'{self.host}/Users/Me', timeout=self.timeout)
        if response.status_code in (401, 403):
            logger.error('Jellyfin rejected the API key (HTTP %s)', response.status_code)
            return False
        if response.ok:
            return True
        info = self._session.get(f'{self.host}/System/Info', timeout=self.timeout)
        if info.status_code in (401, 403):
            logger.error('Jellyfin rejected the API key (HTTP %s)', info.status_code)
            return False
        info.raise_for_status()
        return True

    # ------------------------------------------------------------------
    # Catalog
    # ------------------------------------------------------------------

    @staticmethod
    def _catalog_params(**extra):
        """Query parameters for every catalog list request.

        Per-item user data and all image types except the primary tag are
        dropped so catalog payloads stay small on resource-constrained
        hardware.
        """
        params = {
            'EnableUserData': 'false',
            'EnableImageTypes': 'Primary',
            'ImageTypeLimit': '1',
        }
        params.update(extra)
        return params

    def _get_json(self, path: str, params=None) -> dict:
        self._ensure_token()
        url = f'{self.host}{path}'
        response = self._session.get(url, params=params, timeout=self.timeout)
        if response.status_code in (401, 403) and (self.username or self.password):
            # The user token may have expired; log in again and retry once.
            if self.authenticate_user():
                response = self._session.get(
                    url, params=params, timeout=self.timeout)
        response.raise_for_status()
        return response.json()

    def get_items_in_folder(self, parent_id: str) -> list:
        """Return the direct children of a Jellyfin folder/item."""
        params = self._catalog_params(parentId=parent_id, Recursive='false')
        data = self._get_json('/Items', params=params)
        return data.get('Items') or []

    def get_albums(self, limit: Optional[int] = None, start_index: Optional[int] = None) -> list:
        """Return all music albums on the server (recursive query)."""
        params = self._catalog_params(
            includeItemTypes='MusicAlbum',
            Recursive='true',
        )
        if limit is not None:
            params['Limit'] = limit
        if start_index is not None:
            params['StartIndex'] = start_index
        data = self._get_json('/Items', params=params)
        return data.get('Items') or []

    def get_album_children(self, album_id: str) -> list:
        """Return the audio items directly inside an album."""
        params = self._catalog_params(
            parentId=album_id,
            Recursive='false',
            includeItemTypes='Audio',
        )
        data = self._get_json('/Items', params=params)
        return data.get('Items') or []

    def get_item(self, item_id: str) -> dict:
        """Return the metadata for a single item.

        Falls back to the equivalent ``/Items?Ids=...`` list query when the
        single-item route is rejected by the server.
        """
        try:
            return self._get_json(f'/Items/{item_id}')
        except requests.RequestException:
            params = self._catalog_params(Ids=item_id, Recursive='false')
            data = self._get_json('/Items', params=params)
            items = data.get('Items') or []
            return items[0] if items else {}

    def search(self, query: str, limit: Optional[int] = None, start_index: Optional[int] = None) -> list:
        """Search the library and return the hint results."""
        params = {'searchTerm': query}
        if limit is not None:
            params['Limit'] = limit
        if start_index is not None:
            params['StartIndex'] = start_index
        data = self._get_json('/Search/Hints', params=params)
        return data.get('SearchHints') or []

    # ------------------------------------------------------------------
    # Playback and cover art
    # ------------------------------------------------------------------

    def get_stream_url(self, item_id: str) -> str:
        """Build the static HTTP stream URL for an audio item.

        ``static=true`` requests a direct, untranscoded stream that MPD can
        play. The URL carries the API key and is therefore only pushed into
        the MPD playlist; it must never surface on an RPC/publish channel.
        """
        return f'{self.host}/Audio/{item_id}/stream?static=true&api_key={self.api_key}'

    def get_coverart_bytes(self, item_id: str, max_size: int = 300) -> bytes:
        """Download the primary cover image of an item through the session."""
        self._ensure_token()
        url = (
            f'{self.host}/Items/{item_id}/Images/Primary'
            f'?maxHeight={max_size}&maxWidth={max_size}'
        )
        response = self._session.get(url, timeout=self.timeout)
        if response.status_code in (401, 403) and (self.username or self.password):
            # The user token may have expired; log in again and retry once.
            if self.authenticate_user():
                response = self._session.get(url, timeout=self.timeout)
        response.raise_for_status()
        return response.content

    def close(self) -> None:
        """Close the underlying HTTP session."""
        self._session.close()
