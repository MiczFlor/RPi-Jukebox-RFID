import logging
import subprocess
import components.player
import jukebox.cfghandler
import jukebox.plugs as plugs

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
    logger.debug(f"Folder {folder}. syncing")

    _sync_mode = cfg_sync_shared.getn('sync_shared', 'mode')
    _sync_remote_path = cfg_sync_shared.getn('sync_shared', _sync_mode, 'path')

    _src_path = _clean_trailing_slash(f"{_sync_remote_path}/audiofolders/{folder}") + "/"
    _dst_path = _clean_trailing_slash(components.player.get_music_library_path()) + "/"
    # rsync_changes=$(rsync --compress --recursive --itemize-changes --safe-links --times --omit-dir-times --delete --prune-empty-dirs -
    #                   -filter='-rp folder.conf' --exclude='placeholder' --exclude='.*/' --exclude='@*/'
    #                   "${ssh_port[@]}" "${ssh_conn}""${src_path}" "${dst_path}")

    logger.debug(f"Src: {_src_path} -> Dst: {_dst_path}")
    res = subprocess.run(f"rsync --compress --recursive --itemize-changes --safe-links --times --omit-dir-times --delete --prune-empty-dirs --filter='-rp folder.conf' --exclude='placeholder' --exclude='.*/' --exclude='@*/' {_src_path} {_dst_path}",
                shell=True, check=False, capture_output=True, text=True)
    if res.stderr != b'':
        logger.error(f"Sync Error: {res.stderr}")
    if res.returncode == 0 and res.stdout != '':
        logger.debug(f"synced: {res.stdout}")



def _clean_trailing_slash(path: str):
    cleaned_path = path
    if path.endswith('/'):
        cleaned_path = path[:-1]
    return cleaned_path

