"""HTTP client for the Jellyfin REST API.

The client is a pure HTTP wrapper: username/password login, authenticated
catalog queries, stream URL generation and cover-art downloads. It holds no
player state and never logs the password, the access token or a stream URL.

The login token is bound to the user's library permissions, so a restricted
user only ever sees the content that user is allowed to access.
"""

import logging
import threading
from typing import Optional
from urllib.parse import urlunsplit

import requests

import jukebox


logger = logging.getLogger('jb.player.jellyfin')

#: Default request timeout in seconds for all Jellyfin API calls.
DEFAULT_TIMEOUT = 30.0

#: Client identification reported in the Authorization header. Jellyfin 12
#: reads client, device, device id and version from that header only; a login
#: request without these fields is rejected.
CLIENT_NAME = 'Phoniebox'
DEVICE_NAME = 'Phoniebox'

#: Application version reported to Jellyfin for this device entry. It is
#: derived from jukebox.version() so the reported version cannot drift from
#: the shipped one.
CLIENT_VERSION = jukebox.version()

#: Device id used when no per-installation id is configured. Jellyfin keys
#: devices by (DeviceId, user), so configure_jellyfin() resolves a
#: per-installation id from the token store instead of relying on this
#: constant.
DEFAULT_DEVICE_ID = 'phoniebox'

#: Authorization header without and with a user token. The scheme must be
#: MediaBrowser; the Emby scheme is a legacy form.
AUTH_HEADER_TEMPLATE = (
    'MediaBrowser Client="{client}", Device="{device}", '
    'DeviceId="{device_id}", Version="{version}"'
)
AUTH_HEADER_WITH_TOKEN_TEMPLATE = (
    'MediaBrowser Client="{client}", Device="{device}", '
    'DeviceId="{device_id}", Version="{version}", Token="{token}"'
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


class JellyfinAuthError(requests.RequestException):
    """Raised when the login is not configured or the server rejected it.

    Subclasses requests.RequestException so call sites that already handle
    transport failures keep working unchanged.
    """


def _auth_header(device_id, token=None):
    """Build the Authorization header value, with or without a token."""
    values = {
        'client': CLIENT_NAME,
        'device': DEVICE_NAME,
        'device_id': device_id or DEFAULT_DEVICE_ID,
        'version': CLIENT_VERSION,
    }
    if token is None:
        return AUTH_HEADER_TEMPLATE.format(**values)
    return AUTH_HEADER_WITH_TOKEN_TEMPLATE.format(token=token, **values)


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
    """Small authenticated client for the Jellyfin 12 REST API.

    :param host: Base URL of the Jellyfin server (e.g. http://jellyfin.local:8096).
    :param username: Jellyfin user name used for the login flow.
    :param password: Password belonging to username.
    :param session: Optional requests.Session; tests inject a fake one.
    :param timeout: Request timeout in seconds.
    :param token_store: Optional store that keeps the login token, the
        identity it was issued for and the device id across daemon restarts.
    :param device_id: Per-installation Jellyfin device id; falls back to
        DEFAULT_DEVICE_ID when omitted.
    """

    def __init__(self, host, username='', password='', *, session=None,
                 timeout=DEFAULT_TIMEOUT, token_store=None, device_id=None):
        host = (host or '').strip()
        # A scheme-less host (e.g. "192.168.178.26:8096") is treated as plain
        # HTTP so that requests can build a valid URL.
        if host and '://' not in host:
            host = f'http://{host}'
        self.host = host.rstrip('/')
        self.username = username or ''
        self.password = password or ''
        self._access_token = None
        self._user_id = None
        self._auth_lock = threading.Lock()
        self._token_store = token_store
        self._device_id = device_id or DEFAULT_DEVICE_ID
        self.timeout = timeout
        self._session = session if session is not None else requests.Session()
        self._session.headers.update({
            'Content-Type': 'application/json',
            'Authorization': _auth_header(self._device_id),
        })
        if token_store is not None:
            token, user_id = token_store.load(self.username, self._device_id)
            if token:
                # A stored token keeps the device entry and the previously
                # queued stream URLs valid and skips the login round trip. It
                # is verified on first use: a rejected token triggers a fresh
                # login (see _get_json). The store never returns a token that
                # was issued for another user or device.
                self._set_token(token, user_id)

    def _set_token(self, token, user_id=None):
        """Use token for every subsequent request."""
        self._access_token = token
        self._user_id = user_id
        self._session.headers['Authorization'] = _auth_header(
            self._device_id, token)

    # ------------------------------------------------------------------
    # Authentication
    # ------------------------------------------------------------------

    def authenticate_user(self) -> bool:
        """Log in with the configured user and store the resulting token.

        The token is scoped to the user's library permissions, so catalog and
        playback requests only ever return content that user may access.
        Returns ``False`` when the server rejects the credentials (HTTP
        401/403). Network and transport failures are raised as
        ``requests.RequestException``. Credentials are never logged.
        """
        with self._auth_lock:
            return self._login()

    def _login(self) -> bool:
        """Perform the login request; the caller holds _auth_lock."""
        if not self.username or not self.password:
            logger.error('Jellyfin login requires a username and a password')
            return False
        response = self._session.post(
            f'{self.host}/Users/AuthenticateByName',
            json={'Username': self.username, 'Pw': self.password},
            timeout=self.timeout,
        )
        if response.status_code in (401, 403):
            logger.error(
                'Jellyfin rejected the credentials (HTTP %s)',
                response.status_code)
            return False
        response.raise_for_status()
        data = response.json()
        token = str(data.get('AccessToken') or '').strip()
        if not token:
            logger.error('Jellyfin login response contained no access token')
            return False
        user_id = str((data.get('User') or {}).get('Id') or '')
        self._set_token(token, user_id)
        if self._token_store is not None:
            try:
                self._token_store.save(
                    token, user_id, self.username, self._device_id)
            except OSError as error:
                # The login itself succeeded. Failing to persist the token
                # only costs a second login after the next restart, so it must
                # not propagate into the playback path.
                logger.warning(
                    "Could not persist the Jellyfin token in '%s': %s",
                    self._token_store.path, error)
        logger.info('Jellyfin user logged in')
        return True

    def _ensure_auth(self):
        """Ensure a valid user token is available, logging in on first use.

        Authentication is lazy so that an unreachable server or bad
        credentials cannot block daemon startup. Raises JellyfinAuthError when
        the login flow is not configured or fails.
        """
        if self._access_token:
            return
        if not self.username or not self.password:
            raise JellyfinAuthError(
                'Jellyfin requires a username and a password for the login flow')
        with self._auth_lock:
            if self._access_token:
                # Another thread logged in while this one waited.
                return
            if not self._login():
                raise JellyfinAuthError('Jellyfin login failed')

    def _refresh_auth(self, rejected_token) -> bool:
        """Log in again after HTTP 401; the caller retries once when True."""
        # Concurrent callers can both see a 401 for the same token. Without
        # the generation check below, the second caller would log in again and
        # replace the device and the session the first caller has just
        # created. Only the caller whose token is still the current one
        # performs the login; the others merely retry with the newer token.
        with self._auth_lock:
            if self._access_token != rejected_token:
                return True
            self._access_token = None
            if self._token_store is not None:
                try:
                    self._token_store.clear()
                except OSError as error:
                    # A token file that cannot be written costs at most a
                    # second login after the next restart and must not
                    # propagate out of the request path.
                    logger.warning(
                        "Could not clear the Jellyfin token file '%s': %s",
                        self._token_store.path, error)
            if not self.username or not self.password:
                return False
            return self._login()

    # ------------------------------------------------------------------
    # Catalog
    # ------------------------------------------------------------------

    def _catalog_params(self, **extra):
        """Query parameters shared by every catalog list request.

        Per-item user data and all image types except the primary tag are
        dropped so catalog payloads stay small on resource-constrained
        hardware. userId is sent explicitly: Jellyfin falls back to the
        token's own user when it is omitted, and stating it keeps the user
        scope visible in every request.
        """
        params = {
            'EnableUserData': 'false',
            'EnableImageTypes': 'Primary',
            'ImageTypeLimit': '1',
        }
        if self._user_id:
            params['userId'] = self._user_id
        params.update(extra)
        return params

    def _get_json(self, path: str, params=None) -> dict:
        """Run a GET request and return the decoded JSON body."""
        self._ensure_auth()
        url = f'{self.host}{path}'
        rejected_token = self._access_token
        response = self._session.get(url, params=params, timeout=self.timeout)
        if response.status_code == 401 and self._refresh_auth(rejected_token):
            # The token was revoked server side or came from a stale token
            # file; retry once with a fresh one.
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

        Falls back to the equivalent /Items?Ids=... list query when the
        single-item route is rejected by the server.
        """
        try:
            return self._get_json(f'/Items/{item_id}')
        except JellyfinAuthError:
            # A failed login cannot be recovered through the fallback route.
            raise
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

        static=true requests a direct, untranscoded stream that MPD can play.
        MPD cannot send an Authorization header, so the access token travels
        in the ApiKey query parameter, which is the documented and
        OpenAPI-listed spelling. The endpoint does not currently require a
        token; it is sent so that playback does not depend on that gap and
        keeps working if the server enforces authorization again. The URL is
        only pushed into the MPD playlist and must never surface on an RPC or
        publish channel.

        Unlike a pure URL builder this method performs I/O on the first call
        after a cold start: it authenticates lazily and therefore raises
        JellyfinAuthError or requests.RequestException. Callers must invoke it
        inside an error-guarded block, so that an unreachable server or
        rejected credentials degrade to a logged error instead of propagating
        out of the playback path.
        """
        self._ensure_auth()
        return (
            f'{self.host}/Audio/{item_id}/stream'
            f'?static=true&ApiKey={self._access_token}'
        )

    def get_coverart_bytes(self, item_id: str, max_size: int = 300) -> bytes:
        """Download the primary cover image of an item."""
        self._ensure_auth()
        url = (
            f'{self.host}/Items/{item_id}/Images/Primary'
            f'?maxHeight={max_size}&maxWidth={max_size}'
        )
        rejected_token = self._access_token
        response = self._session.get(url, timeout=self.timeout)
        if response.status_code == 401 and self._refresh_auth(rejected_token):
            response = self._session.get(url, timeout=self.timeout)
        response.raise_for_status()
        return response.content

    def close(self) -> None:
        """Close the underlying HTTP session."""
        self._session.close()
