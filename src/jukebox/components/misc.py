"""
Miscellaneous function package
"""
import os
import time
import logging.handlers
import jukebox
import jukebox.plugs as plugin
import jukebox.utils
from jukebox.daemon import get_jukebox_daemon
import jukebox.cfghandler

logger = logging.getLogger('jb.misc')
cfg = jukebox.cfghandler.get_handler('jukebox')


@plugin.register
def rpc_cmd_help():
    """Return all commands for RPC"""
    return plugin.summarize()


@plugin.register
def get_all_loaded_packages():
    """Get all successfully loaded plugins"""
    return plugin.get_all_loaded_packages()


@plugin.register
def get_all_failed_packages():
    """Get all plugins with error during load or initialization"""
    return plugin.get_all_failed_packages()


@plugin.register
def get_start_time():
    """Time when JukeBox has been started"""
    return time.ctime(get_jukebox_daemon().start_time)


def get_log(handler_name: str):
    """Get the log file from the loggers (debug_file_handler, error_file_handler)"""
    # With the correct logger.yaml, there is up to two RotatingFileHandler attached
    content = "No file handles configured"
    for h in logging.getLogger('jb').handlers:
        if isinstance(h, logging.handlers.RotatingFileHandler):
            content = f"No file handler with name {handler_name} configured"
            if h.name == handler_name:
                try:
                    size = os.path.getsize(h.baseFilename)
                    if size == 0:
                        content = f"Log file {h.baseFilename} is empty. (Could be good or bad: " \
                                  "Is the RotatingFileHandler configured as handler sink for jb in logger.yaml?)"
                        break
                    mtime = os.path.getmtime(h.baseFilename)
                    stime = get_jukebox_daemon().start_time
                    logger.debug(f"Accessing log file {h.baseFilename} modified time {time.ctime(mtime)} "
                                 f"(JB start time {time.ctime(stime)})")
                    # Generous 3 second tolerance between file creation and jukebox start time recording
                    if mtime - stime < -3:
                        content = (f"Log file {h.baseFilename} too old for this Jukebox start! "
                                   f"Is the RotatingFileHandler configured as handler sink for jb in logger.yaml?")
                        break
                    with open(h.baseFilename) as stream:
                        content = stream.read()
                except Exception as e:
                    content = f"{e.__class__.__name__}: {e}"
                    logger.error(content)
                break
    return content


@plugin.register
def get_log_debug():
    """Get the log file (from the debug_file_handler)"""
    return get_log('debug_file_handler')


@plugin.register
def get_log_error():
    """Get the log file (from the error_file_handler)"""
    return get_log('error_file_handler')


@plugin.register
def get_version():
    return jukebox.version()


@plugin.register
def get_git_state():
    """Return git state information for the current branch"""
    return get_jukebox_daemon().git_state


@plugin.register
def empty_rpc_call(msg: str = ''):
    """This function does nothing.

    The RPC command alias 'none' is mapped to this function.

    This is also used when configuration errors lead to non existing RPC command alias definitions.
    When the alias definition is void, we still want to return a valid function to simplify error handling
    up the module call stack.

    :param msg: If present, this message is send to the logger with severity warning
    """
    if msg:
        logger.warning(msg)


@plugin.register
def get_app_settings():
    """Return settings for web app stored in jukebox.yaml"""
    show_covers = cfg.setndefault('webapp', 'show_covers', value=True)

    return {
        'show_covers': show_covers
    }


@plugin.register
def set_app_settings(settings={}):
    """Set configuration settings for the web app."""
    for key, value in settings.items():
        cfg.setn('webapp', key, value=value)


#: Editable Jellyfin plugin configuration keys (``players.jellyfin``) with
#: their defaults. Used by the web app settings section.
JELLYFIN_SETTINGS_DEFAULTS = {
    'enabled': False,
    'host': '',
    'api_key': '',
    'username': '',
    'password': '',
    'catalog_cache_ttl': 300,
    'request_timeout': 30,
}

#: Keys whose stored value is a secret. They are never returned to the web
#: app and only overwritten when a new non-empty value is submitted.
JELLYFIN_SECRET_KEYS = frozenset({'api_key', 'password'})

#: Keys that must be positive numbers.
JELLYFIN_NUMERIC_KEYS = frozenset({'catalog_cache_ttl', 'request_timeout'})


@plugin.register
def get_jellyfin_settings() -> dict:
    """Return the Jellyfin plugin configuration for the web app.

    Secret values (``api_key``, ``password``) are never returned. Only a
    boolean per secret (``has_api_key``, ``has_password``) tells the UI
    whether a value is currently configured, so it can indicate the set
    state without ever revealing the secret itself.
    """
    settings = {}
    for key, default in JELLYFIN_SETTINGS_DEFAULTS.items():
        value = cfg.setndefault('players', 'jellyfin', key, value=default)
        if key in JELLYFIN_SECRET_KEYS:
            settings[f'has_{key}'] = bool(value)
        else:
            settings[key] = value
    return settings


def _jellyfin_merged(settings):
    """Merge submitted settings with the stored ones and validate them.

    Secret values are only replaced by a new non-empty value; an empty or
    absent secret keeps the stored value. Numeric settings must be positive
    numbers. Raises :class:`ValueError` for unknown keys or invalid values.
    """
    if not isinstance(settings, dict):
        raise ValueError('Jellyfin settings must be an object')

    unknown = set(settings) - set(JELLYFIN_SETTINGS_DEFAULTS)
    if unknown:
        raise ValueError(
            f"Unknown Jellyfin setting(s): {', '.join(sorted(unknown))}")

    merged = {}
    for key in JELLYFIN_SETTINGS_DEFAULTS:
        current = cfg.getn(
            'players', 'jellyfin', key,
            default=JELLYFIN_SETTINGS_DEFAULTS[key])
        if key in JELLYFIN_SECRET_KEYS:
            merged[key] = settings.get(key) or current
        else:
            merged[key] = settings.get(key, current)

    for key in JELLYFIN_NUMERIC_KEYS:
        try:
            parsed = float(merged[key])
        except (TypeError, ValueError):
            raise ValueError(
                f"Jellyfin setting '{key}' must be a number") from None
        if parsed <= 0:
            raise ValueError(f"Jellyfin setting '{key}' must be positive")
        merged[key] = parsed
    return merged


def _validate_jellyfin_enabled(merged):
    """Mirror ``configure_jellyfin`` requirements for an enabled setup."""
    if not merged['enabled']:
        return
    if not str(merged['host'] or '').strip():
        raise ValueError('Jellyfin is enabled but no server host is set')
    if not merged['api_key'] and not (
            merged['username'] and merged['password']):
        raise ValueError(
            'Jellyfin is enabled but neither an API key nor a '
            'username/password pair is set')


@plugin.register
def set_jellyfin_settings(settings={}) -> dict:
    """Set the Jellyfin plugin configuration for the web app.

    Only known keys are accepted. Secret values (``api_key``, ``password``)
    are only overwritten when a new non-empty value is submitted, so the UI
    never has to know (or send back) the stored secret; an empty value
    leaves it untouched. The merged result is validated like
    ``configure_jellyfin`` and persisted to ``jukebox.yaml``.
    """
    merged = _jellyfin_merged(settings)
    _validate_jellyfin_enabled(merged)
    for key, value in merged.items():
        cfg.setn('players', 'jellyfin', key, value=value)
    if cfg.loaded_from is not None:
        cfg.save(only_if_changed=True)
    return get_jellyfin_settings()


@plugin.register
def test_jellyfin_connection(host='', timeout=3.0) -> dict:
    """Probe a Jellyfin server address, trying the standard combinations.

    An incomplete address (no scheme and/or no port) is expanded to the
    standard Jellyfin combinations (http/https x ports 8096/8920) and
    every candidate is probed at its public system-info endpoint. Returns
    whether a server was found, the matching URL (or ``None``) and the
    list of candidates that were tried.
    """
    from components.jellyfin.jellyfin_api_client import (
        expand_jellyfin_host, probe_jellyfin_host)
    candidates = expand_jellyfin_host(host)
    found = probe_jellyfin_host(
        candidates, timeout=timeout) if candidates else None
    return {
        'found': found is not None,
        'url': found,
        'candidates': candidates,
    }
