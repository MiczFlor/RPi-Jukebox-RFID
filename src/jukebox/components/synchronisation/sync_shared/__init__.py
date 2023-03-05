import logging
import jukebox.cfghandler
import jukebox.plugs as plugin
import components.rfid.reader
import components.synchronisation.sync_shared as sync_shared

logger = logging.getLogger('jb.synchronisation.sync_shared')

cfg_main = jukebox.cfghandler.get_handler('jukebox')
cfg_sync_shared = jukebox.cfghandler.get_handler('sync_shared')

@plugin.initialize
def initialize():
    if cfg_main.setndefault('sync_shared', 'enable', value=False):
        config_file = cfg_main.setndefault('sync_shared', 'config_file', value='../../shared/settings/sync_shared.yaml')
        try:
            jukebox.cfghandler.load_yaml(cfg_sync_shared, config_file)
        except Exception as e:
            logger.error(f"Error loading sync_shared config file. {e.__class__.__name__}: {e}")
            return

        components.rfid.reader.rfid_card_detect_callbacks.register(sync_shared.rfid_card_detect_callback)
