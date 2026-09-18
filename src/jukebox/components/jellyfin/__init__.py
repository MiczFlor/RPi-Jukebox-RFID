"""Jellyfin player backend registration and configuration."""

import logging
import uuid

import jukebox.cfghandler

from .jellyfin_api_client import DEFAULT_TIMEOUT, JellyfinApiClient
from .jellyfin_backend import JellyfinBackend
from .jellyfin_token_store import JellyfinTokenStore


logger = logging.getLogger('jb.player.jellyfin')
_jellyfin_backend = None

#: Default seconds the Jellyfin album catalog is cached before a refresh.
DEFAULT_CATALOG_CACHE_TTL = 300


def _resolve_device_id(token_store, configured):
    """Return the device id for this installation.

    components.player is loaded with ignore_errors=True, so an exception here
    would take down MPD, Spotify and Jellyfin playback at once. A token file
    that cannot be written must therefore degrade to a process-lifetime id
    instead of aborting start-up.
    """
    try:
        return token_store.device_id(configured)
    except OSError as error:
        logger.warning(
            "Could not persist the Jellyfin device id in '%s' (%s); using a "
            "temporary id for this run. The access token cannot be persisted "
            "either, so the next start logs in again.",
            token_store.path, error)
        return str(configured or '').strip() or uuid.uuid4().hex


def _positive_float(value, default):
    """Parse ``value`` as a positive float, falling back to ``default``.

    Invalid or non-positive configuration values (e.g. a typo in jukebox.yaml)
    must never raise during plugin initialization: the player plugin is loaded
    with ``ignore_errors=True``, so a single bad value would otherwise take
    down MPD/Spotify/Jellyfin playback entirely.
    """
    try:
        parsed = float(value)
    except (TypeError, ValueError):
        logger.warning(
            "Invalid players.jellyfin numeric value %r; using default %s",
            value, default)
        return default
    if parsed <= 0:
        logger.warning(
            "Non-positive players.jellyfin value %r; using default %s",
            value, default)
        return default
    return parsed


def configure_jellyfin(player_ctrl):
    """Create the Jellyfin backend and register it when enabled.

    Registration is a no-op unless ``players.jellyfin.enabled`` is set.
    Authentication is lazy: the credentials are checked on the first catalog
    or playback request, not at startup.
    """
    global _jellyfin_backend
    cfg = jukebox.cfghandler.get_handler('jukebox')

    enabled = cfg.setndefault('players', 'jellyfin', 'enabled', value=False)
    host = cfg.setndefault('players', 'jellyfin', 'host', value='')
    username = cfg.setndefault('players', 'jellyfin', 'username', value='')
    password = cfg.setndefault('players', 'jellyfin', 'password', value='')
    token_file = cfg.setndefault(
        'players', 'jellyfin', 'token_file',
        value='../../shared/settings/jellyfin_token.json')
    # Jellyfin logs out every device of the same user with the same device id,
    # so each installation needs its own stable id. Empty generates one on
    # first use and stores it in the token file.
    configured_device_id = cfg.setndefault(
        'players', 'jellyfin', 'device_id', value='')
    cache_ttl = _positive_float(
        cfg.setndefault('players', 'jellyfin', 'catalog_cache_ttl',
                        value=DEFAULT_CATALOG_CACHE_TTL)
        or DEFAULT_CATALOG_CACHE_TTL,
        DEFAULT_CATALOG_CACHE_TTL)
    request_timeout = _positive_float(
        cfg.setndefault('players', 'jellyfin', 'request_timeout',
                        value=DEFAULT_TIMEOUT) or DEFAULT_TIMEOUT,
        DEFAULT_TIMEOUT)

    if not enabled:
        return None
    if not host:
        logger.error(
            "Jellyfin enabled but host missing; backend not registered")
        return None
    if not username or not password:
        logger.error(
            "Jellyfin enabled but username/password incomplete; backend not "
            "registered. The login requires a username and a password.")
        return None

    token_store = JellyfinTokenStore(token_file)
    api = JellyfinApiClient(
        host, username=username, password=password,
        timeout=request_timeout,
        token_store=token_store,
        device_id=_resolve_device_id(token_store, configured_device_id))

    backend = JellyfinBackend(api, player_ctrl._get_backend('mpd'), cache_ttl)
    player_ctrl.register_backend('jellyfin', backend)
    _jellyfin_backend = backend
    backend.start_warmup()
    # MPD restores its queue across a restart, so a Jellyfin stream can
    # already be playing when the daemon starts. That playback is reported
    # by this backend, which owns the metadata and the cover.
    backend.start_restore(lambda: player_ctrl.adopt_backend('jellyfin'))
    logger.info("Jellyfin backend registered")
    return backend
