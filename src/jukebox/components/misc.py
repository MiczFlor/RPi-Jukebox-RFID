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
