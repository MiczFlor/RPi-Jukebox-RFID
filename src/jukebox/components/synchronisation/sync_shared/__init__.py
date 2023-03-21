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


class SyncShared:
    """Control class for sync shared functionality"""

    def __init__(self):
        self._sync_enabled = cfg_main.setndefault('sync_shared', 'enable', value=False) is True
        if self._sync_enabled:
            logger.info("Sync shared activated")
            config_file = cfg_main.setndefault('sync_shared', 'config_file', value='../../shared/settings/sync_shared.yaml')
            try:
                jukebox.cfghandler.load_yaml(cfg_sync_shared, config_file)
            except Exception as e:
                logger.error(f"Error loading sync_shared config file. {e.__class__.__name__}: {e}")
                return

            self._sync_on_rfid_scan_enabled = (cfg_sync_shared.getn('sync_shared', 'on_rfid_scan_enabled', default=False)
                                               is True)
            if not self._sync_on_rfid_scan_enabled:
                logger.info("Sync on RFID scan deactivated")
            self._sync_mode = cfg_sync_shared.getn('sync_shared', 'mode')
            self._sync_remote_server = cfg_sync_shared.getn('sync_shared', self._sync_mode, 'server')
            self._sync_remote_port = int(cfg_sync_shared.getn('sync_shared', self._sync_mode, 'port'))
            self._sync_remote_timeout = int(cfg_sync_shared.getn('sync_shared', self._sync_mode, 'timeout'))
            self._sync_remote_path = cfg_sync_shared.getn('sync_shared', self._sync_mode, 'path')

            self._sync_is_mode_ssh = self._sync_mode == "ssh"
            if self._sync_is_mode_ssh:
                self._sync_remote_ssh_user = cfg_sync_shared.getn('sync_shared', self._sync_mode, 'username')

        else:
            logger.info("Sync shared deactivated")

    def __exit__(self):
        cfg_sync_shared.save(only_if_changed=True)

    @plugs.tag
    def sync_full(self) -> bool:
        """
        Sync full from the remote server
        """

        if self._sync_enabled:
            logger.info("Syncing full")
            _files_synced = self._sync_folder('')

        else:
            logger.debug("Sync shared deactivated")

        return _files_synced

    @plugs.tag
    def sync_change_on_rfid_scan(self, option: str='toggle') -> None:
        """
        Change activation of 'on_rfid_scan_enabled'

        :param option: Must be one of 'true', 'false', 'toggle'
        """
        if self._sync_enabled:

            if option == 'true':
                _new_state = True
            elif option == 'false':
                _new_state = False
            elif option == 'toggle':
                _new_state = not self._sync_on_rfid_scan_enabled
            else:
                logger.error("Invalid value for 'option'")
                _new_state = False

            cfg_sync_shared.setn('sync_shared', 'on_rfid_scan_enabled', value=_new_state)
            self._sync_on_rfid_scan_enabled = _new_state

            logger.info(f"Changed 'on_rfid_scan_enabled' to '{_new_state}'")

        else:
            logger.debug("Sync shared deactivated")

    @plugs.tag
    def sync_card_database(self, path: str):
        logger.debug(f"Sync Database {path}.")

    @plugs.tag
    def sync_folder(self, folder: str) -> bool:
        """
        Sync the folder from the remote server, if existing

        :param folder: Folder path relative to music library path
        """
        _files_synced = False

        if self._sync_enabled:
            if self._sync_on_rfid_scan_enabled:
                logger.info(f"Syncing Folder '{folder}'")
                _files_synced = self._sync_folder(folder)

            else:
                logger.debug("Sync on RFID scan deactivated")

        else:
            logger.debug("Sync shared deactivated")

        return _files_synced

    def _sync_folder(self, folder: str) -> bool:
        _files_synced = False

        if self._is_server_reachable():
            _sync_remote_path_audio = os.path.join(self._sync_remote_path, "audiofolders")
            _music_library_path = components.player.get_music_library_path()
            _cleaned_foldername = self._clean_foldername(_music_library_path, folder)
            _src_path = self._ensure_trailing_slash(os.path.join(_sync_remote_path_audio, _cleaned_foldername))
            # TODO fix general absolut/relativ folder path handling
            _dst_path = self._ensure_trailing_slash(os.path.join(_music_library_path, folder))

            if self._is_dir(_src_path):
                _files_synced = self._sync_paths(_src_path, _dst_path)

            else:
                logger.warn(f"Folder does not exist remote: {_src_path}")

        return _files_synced

    def _sync_paths(self, src_path: str, dst_path: str) -> bool:
        _files_synced = False
        logger.debug(f"Src: '{src_path}' -> Dst: '{dst_path}'")

        if dst_path.endswith('/'):
            os.makedirs(dst_path, exist_ok=True)

        if self._sync_is_mode_ssh:
            _user = self._sync_remote_ssh_user
            _host = self._sync_remote_server
            _port = self._sync_remote_port

            _paths = ['-e', f"ssh -p {_port}", f"{_user}@{_host}:'{src_path}'", dst_path]

        else:
            _paths = [src_path, dst_path]

        _run_params = (['rsync',
                        '--compress', '--recursive', '--itemize-changes',
                        '--safe-links', '--times', '--omit-dir-times',
                        '--delete', '--prune-empty-dirs',
                        '--filter=-rp folder.conf',
                        '--exclude=.*', '--exclude=.*/', '--exclude=@*/', '--cvs-exclude'
                        ] + _paths)

        _runresult = subprocess.run(_run_params, shell=False, check=False, capture_output=True, text=True)

        if _runresult.returncode == 0 and _runresult.stdout != '':
            logger.debug(f"Synced:\n{_runresult.stdout}")
            _files_synced = True
        if _runresult.stderr != '':
            logger.error(f"Sync Error: {_runresult.stderr}")

        return _files_synced

    def _is_server_reachable(self) -> bool:
        _host = self._sync_remote_server
        _port = self._sync_remote_port
        _timeout = self._sync_remote_timeout

        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(_timeout)
            result = sock.connect_ex((_host, _port))
        except Exception as e:
            logger.error(f"Server not reachable: {_host}:{_port}. {e.__class__.__name__}: {e}")
            return False

        _server_reachable = result == 0
        if not _server_reachable:
            logger.error(f"Server not reachable: {_host}:{_port}. errorcode: {result}")

        return _server_reachable

    def _is_dir(self, path: str) -> bool:
        if self._sync_is_mode_ssh:
            _user = self._sync_remote_ssh_user
            _host = self._sync_remote_server
            _port = self._sync_remote_port

            _runresult = subprocess.run(['ssh',
                                    f"{_user}@{_host}", f"-p {_port}",
                                    '[', '-d', f"'{path}'", ']'],
                                shell=False, check=False, capture_output=True, text=True)

            _result = _runresult.returncode == 0

        else:
            _result = os.path.isdir(path)

        return _result

    def _clean_foldername(self, lib_path: str, folder: str) -> str:
        _folder = folder.removeprefix(lib_path)
        _folder = self._remove_leading_slash(self._remove_trailing_slash(_folder))
        return _folder

    def _ensure_trailing_slash(self, path: str) -> str:
        _path = path
        if not _path.endswith('/'):
            _path = _path + '/'
        return _path

    def _remove_trailing_slash(self, path: str) -> str:
        _path = path.removesuffix('/')
        return _path

    def _remove_leading_slash(self, path: str) -> str:
        _path = path.removeprefix('/')
        return _path

# ---------------------------------------------------------------------------
# Plugin Initializer / Finalizer
# ---------------------------------------------------------------------------


sync_shared_ctrl: SyncShared


@plugs.initialize
def initialize():
    global sync_shared_ctrl
    sync_shared_ctrl = SyncShared()
    plugs.register(sync_shared_ctrl, name='ctrl')


@plugs.atexit
def atexit(**ignored_kwargs):
    global sync_shared_ctrl
    return sync_shared_ctrl.__exit__()
