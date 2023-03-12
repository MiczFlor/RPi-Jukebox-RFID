import logging
import subprocess
import components.player
import jukebox.cfghandler
import jukebox.plugs as plugs
import socket
import os

logger = logging.getLogger('jb.sync_shared')

cfg_main = jukebox.cfghandler.get_handler('jukebox')
cfg_sync_shared = jukebox.cfghandler.get_handler('sync_shared')

#TODO create class and init settings
#class SyncShared:
#    """Interface to MPD Music Player Daemon"""


#sync_shared_ctrl: SyncShared

@plugs.initialize
def initialize():
    #global sync_shared_ctrl
    #sync_shared_ctrl = SyncShared()
    #plugs.register(sync_shared_ctrl, name='ctrl')
    if cfg_main.setndefault('sync_shared', 'enable', value=False):
        config_file = cfg_main.setndefault('sync_shared', 'config_file', value='../../shared/settings/sync_shared.yaml')
        try:
            jukebox.cfghandler.load_yaml(cfg_sync_shared, config_file)
        except Exception as e:
            logger.error(f"Error loading sync_shared config file. {e.__class__.__name__}: {e}")
            return

@plugs.register
def sync_card_database(path: str):
    logger.debug(f"Sync Database {path}.")


@plugs.register
def sync_folder(folder: str):
    """
    Sync the folder from the remote server, if existing

    :param folder: Folder path relative to music library path
    """
    logger.info(f"Syncing Folder '{folder}'")
    _files_synced = False

    _sync_mode = cfg_sync_shared.getn('sync_shared', 'mode')
    _sync_remote_server = cfg_sync_shared.getn('sync_shared', _sync_mode, 'server')
    _sync_remote_port = int(cfg_sync_shared.getn('sync_shared', _sync_mode, 'port'))
    _sync_remote_timeout = int(cfg_sync_shared.getn('sync_shared', _sync_mode, 'timeout'))

    if _is_server_reachable(_sync_remote_server, _sync_remote_port, _sync_remote_timeout):
        _sync_remote_path = cfg_sync_shared.getn('sync_shared', _sync_mode, 'path')
        _sync_remote_path_audio =_remove_trailing_slash(_sync_remote_path) + "/audiofolders/"

        if os.path.isdir(_sync_remote_path_audio):
            _cleaned_folder=_remove_leading_slash(_remove_trailing_slash(folder))
            _src_path = _sync_remote_path_audio + _cleaned_folder + "/"

            if os.path.isdir(_src_path):
                _dst_path = _remove_trailing_slash(components.player.get_music_library_path()) + "/" + _cleaned_folder + "/"

                _files_synced = _sync_paths(_src_path, _dst_path)

            else:
                logger.warn(f"Folder does not exist: {_src_path}")

        else:
            logger.error(f"Folder does not exist: {_sync_remote_path_audio}")

    return _files_synced

def _sync_paths(src_path:str, dst_path:str):
    _files_synced = False
    logger.debug(f"Src: '{src_path}' -> Dst: '{dst_path}'")

    if dst_path.endswith('/'):
        os.makedirs(dst_path, exist_ok = True)

    res = subprocess.run(['rsync',
                            '--compress', '--recursive', '--itemize-changes', '--safe-links', '--times', '--omit-dir-times', '--delete', '--prune-empty-dirs',
                            '--filter=-rp folder.conf', "--exclude='.gitkeep'", "--exclude='.*/'", "--exclude='@*/'",
                            src_path, dst_path],
                        shell=False, check=False, capture_output=True, text=True)

    if res.returncode == 0 and res.stdout != '':
        logger.debug(f"Synced:\n{res.stdout}")
        _files_synced = True
    if res.stderr != '':
        logger.error(f"Sync Error: {res.stderr}")

    return _files_synced

def _is_server_reachable(host: str, port: int, timeout: int):
    _port = int(port)
    _timeout = int(timeout)
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(_timeout)
        result = sock.connect_ex((host, _port))
    except Exception as e:
        logger.error(f"Server check failed with {host}:{port}. {e.__class__.__name__}: {e}")
        return False

    _server_reachable = result == 0
    if(not _server_reachable):
        logger.error(f"Server check failed with {host}:{port}. errorcode: {_server_reachable}")

    return _server_reachable


def _remove_trailing_slash(path: str):
    cleaned_path = path
    if path.endswith('/'):
        cleaned_path = path[:-1]
    return cleaned_path

def _remove_leading_slash(path: str):
    cleaned_path = path
    if path.startswith('/'):
        cleaned_path = path[1:]
    return cleaned_path
