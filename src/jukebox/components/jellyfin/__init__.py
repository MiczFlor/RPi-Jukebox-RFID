"""Jellyfin player backend registration and configuration."""

import logging

import jukebox.cfghandler

from .jellyfin_api_client import DEFAULT_TIMEOUT, JellyfinApiClient
from .jellyfin_backend import JellyfinBackend


logger = logging.getLogger('jb.player.jellyfin')
_jellyfin_backend = None

#: Default seconds the Jellyfin album catalog is cached before a refresh.
DEFAULT_CATALOG_CACHE_TTL = 300


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
    Authentication is lazy: neither the API key nor the login credentials
    are validated at startup, only on the first catalog or playback request.
    """
    global _jellyfin_backend
    cfg = jukebox.cfghandler.get_handler('jukebox')
    enabled = cfg.setndefault('players', 'jellyfin', 'enabled', value=False)
    host = cfg.setndefault('players', 'jellyfin', 'host', value='')
    api_key = cfg.setndefault('players', 'jellyfin', 'api_key', value='')
    username = cfg.setndefault('players', 'jellyfin', 'username', value='')
    password = cfg.setndefault('players', 'jellyfin', 'password', value='')
    cache_ttl = _positive_float(
        cfg.setndefault('players', 'jellyfin', 'catalog_cache_ttl',
                        value=DEFAULT_CATALOG_CACHE_TTL) or DEFAULT_CATALOG_CACHE_TTL,
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
    if not api_key and not (username and password):
        logger.error(
            "Jellyfin enabled but neither api_key nor username/password "
            "set; backend not registered")
        return None
    if username or password:
        api = JellyfinApiClient(
            host, username=username, password=password,
            timeout=request_timeout)
    else:
        api = JellyfinApiClient(host, api_key, timeout=request_timeout)
    backend = JellyfinBackend(api, player_ctrl._get_backend('mpd'), cache_ttl)
    player_ctrl.register_backend('jellyfin', backend)
    _jellyfin_backend = backend
    backend.start_warmup()
    logger.info("Jellyfin backend registered")
    return backend
