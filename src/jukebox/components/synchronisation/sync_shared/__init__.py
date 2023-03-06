import logging
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

