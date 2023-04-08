"""
Handles the synchronisation of shared audiofolder and the card database

audiofolder:


card database:
As this is only a single file for all cards (unlike v2.x), it has some specialities.
On synchronisation the remote file will not synced with the original cards database, but rather a local copy.
If a full sync is performed the state is then written back to the original file.
If a single card sync is performed only the state of the specific card id is updated in the original file.
This is done to keep the possibility to play audio offline.
Otherwise we would also update other card ids where the audiofolders have not been synced yet.
The local copy is kept to reduce unnecessary syncing.

"""

import logging
import subprocess
import components.player
import jukebox.cfghandler
import jukebox.plugs as plugs
import socket
import os
import shutil

logger = logging.getLogger('jb.sync_shared')

cfg_main = jukebox.cfghandler.get_handler('jukebox')
cfg_sync_shared = jukebox.cfghandler.get_handler('sync_shared')
cfg_cards = jukebox.cfghandler.get_handler('cards')


class SyncShared:
    """Control class for sync shared functionality"""

    def __init__(self):
        with cfg_main:
            self._sync_enabled = cfg_main.setndefault('sync_shared', 'enable', value=False) is True
        if self._sync_enabled:
            logger.info("Sync shared activated")
            with cfg_main:
                config_file = cfg_main.setndefault('sync_shared', 'config_file',
                                                    value='../../shared/settings/sync_shared.yaml')
            try:
                cfg_sync_shared.load(config_file)
            except Exception as e:
                logger.error(f"Error loading sync_shared config file. {e.__class__.__name__}: {e}")
                return

            with cfg_sync_shared:
                self._sync_on_rfid_scan_enabled = (cfg_sync_shared.getn('sync_shared', 'on_rfid_scan_enabled', default=False)
                                                is True)
                if not self._sync_on_rfid_scan_enabled:
                    logger.info("Sync on RFID scan deactivated")
                self._sync_mode = cfg_sync_shared.getn('sync_shared', 'mode')
                self._sync_remote_server = cfg_sync_shared.getn('sync_shared', 'credentials', 'server')
                self._sync_remote_port = int(cfg_sync_shared.getn('sync_shared', 'credentials', 'port'))
                self._sync_remote_timeout = int(cfg_sync_shared.getn('sync_shared', 'credentials', 'timeout'))
                self._sync_remote_path = cfg_sync_shared.getn('sync_shared', 'credentials', 'path')

                self._sync_is_mode_ssh = self._sync_mode == "ssh"
                if self._sync_is_mode_ssh:
                    self._sync_remote_ssh_user = cfg_sync_shared.getn('sync_shared', 'credentials', 'username')

            components.rfid.reader.rfid_card_detect_callbacks.register(self.rfid_callback)
        else:
            logger.info("Sync shared deactivated")

    def __exit__(self):
        cfg_sync_shared.save(only_if_changed=True)

    def rfid_callback(self, card_id: str, state: int):
        if state == -1:
            self.sync_card_database(card_id)

    @plugs.tag
    def sync_change_on_rfid_scan(self, option: str = 'toggle') -> None:
        """
        Change activation of 'on_rfid_scan_enabled'

        :param option: Must be one of 'enable', 'disable', 'toggle'
        """
        if self._sync_enabled:

            if option == 'enable':
                _new_state = True
            elif option == 'disable':
                _new_state = False
            elif option == 'toggle':
                _new_state = not self._sync_on_rfid_scan_enabled
            else:
                logger.error(f"Invalid value '{option}' for 'option' in 'sync_change_on_rfid_scan'")
                _new_state = None

            if _new_state is not None:
                cfg_sync_shared.setn('sync_shared', 'on_rfid_scan_enabled', value=_new_state)
                self._sync_on_rfid_scan_enabled = _new_state

                logger.info(f"Changed 'on_rfid_scan_enabled' to '{_new_state}'")

        else:
            logger.debug("Sync shared deactivated")

    @plugs.tag
    def sync_all(self) -> bool:
        """
        Sync all audiofolder and cardids from the remote server.
        Removes local entries not existing at the remote server.
        """
        _files_synced = False

        if self._precheck_enablement_sync:
            logger.info("Syncing full")
            _database_synced = self._sync_card_database()
            _folder_synced = self._sync_folder('')
            _files_synced = _database_synced or _folder_synced

        return _files_synced

    @plugs.tag
    def sync_card_database(self, card_id: str) -> bool:
        """
        Sync the card database from the remote server, if existing.
        If card_id is provided only this entry is updated.

        :param card_id: The cardid to update
        """
        _files_synced = False

        if self._precheck_enablement_sync_on_rfid_scan:
            _files_synced = self._sync_card_database(card_id)

        return _files_synced

    @plugs.tag
    def sync_folder(self, folder: str) -> bool:
        """
        Sync the folder from the remote server, if existing

        :param folder: Folder path relative to music library path
        """
        _files_synced = False

        if self._precheck_enablement_sync_on_rfid_scan:
            _files_synced = self._sync_folder(folder)

        return _files_synced

    def _precheck_enablement_sync(self) -> bool:
        if self._sync_enabled:
            return True
        else:
            logger.debug("Sync shared deactivated")

        return False

    def _precheck_enablement_sync_on_rfid_scan(self) -> bool:
        if self._precheck_enablement_sync:
            if self._sync_on_rfid_scan_enabled:
                return True
            else:
                logger.debug("Sync on RFID scan deactivated")

        return False

    def _sync_card_database(self, card_id: str = None) -> bool:
        _card_database_path = cfg_cards.loaded_from
        logger.info(f"Syncing card database: {_card_database_path}")
        _files_synced = False

        if self._is_server_reachable():
            _sync_remote_path_settings = os.path.join(self._sync_remote_path, "settings")
            _card_database_file = os.path.basename(_card_database_path)
            _card_database_dir = os.path.dirname(_card_database_path)
            _src_path = os.path.join(_sync_remote_path_settings, _card_database_file)
            # Sync the card database to a temp file to handle changes of single card ids correctly.
            # This file is kept to reduce unnecessary syncing!
            _dst_path = os.path.join(_card_database_dir, "sync_temp_" + _card_database_file)

            if self._isfile_remote(_src_path):
                _files_synced = self._sync_paths(_src_path, _dst_path)

                if os.path.isfile(_dst_path):
                    # Check even if nothing has been synced,
                    # as the original card database could have been changed locally (e.g. WebUi)
                    if card_id is not None:
                        # This ConfigHandler is explicitly instantiated and only used to read the synced temp database file
                        _cfg_cards_temp = jukebox.cfghandler.ConfigHandler("sync_temp_cards")
                        with _cfg_cards_temp:
                            _cfg_cards_temp.load(_dst_path)
                            _card_entry = _cfg_cards_temp.get(card_id, default=None)
                        if _card_entry is not None:
                            with cfg_cards:
                                cfg_cards[card_id] = _card_entry
                                if cfg_cards.is_modified():
                                    cfg_cards.save(only_if_changed=True)
                                    _files_synced = True
                                    logger.info(f"Updated entry '{card_id}' in '{_card_database_path}'")
                    else:
                        # overwrite original file with synced state
                        with cfg_cards:
                            shutil.copy2(_dst_path, _card_database_path)
                            cfg_cards.load(_card_database_path)
                        logger.info(f"Updated '{_card_database_path}'")

            else:
                logger.warn(f"Card database does not exist remote: {_src_path}")

        return _files_synced

    def _sync_folder(self, folder: str) -> bool:
        logger.info(f"Syncing Folder '{folder}'")
        _files_synced = False

        if self._is_server_reachable():
            _sync_remote_path_audio = os.path.join(self._sync_remote_path, "audiofolders")
            _music_library_path = components.player.get_music_library_path()
            _cleaned_foldername = self._clean_foldername(_music_library_path, folder)
            _src_path = self._ensure_trailing_slash(os.path.join(_sync_remote_path_audio, _cleaned_foldername))
            # TODO fix general absolut/relativ folder path handling
            _dst_path = self._ensure_trailing_slash(os.path.join(_music_library_path, folder))

            if self._isdir_remote(_src_path):
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
                        '--exclude=folder.conf',  # exclude if existing from v2.x
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

    def _isfile_remote(self, path: str) -> bool:
        if self._sync_is_mode_ssh:
            _user = self._sync_remote_ssh_user
            _host = self._sync_remote_server
            _port = self._sync_remote_port

            _runresult = subprocess.run(['ssh',
                                    f"{_user}@{_host}", f"-p {_port}",
                                    '[', '-f', f"'{path}'", ']'],
                                shell=False, check=False, capture_output=True, text=True)

            _result = _runresult.returncode == 0

        else:
            _result = os.path.isfile(path)

        return _result

    def _isdir_remote(self, path: str) -> bool:
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
