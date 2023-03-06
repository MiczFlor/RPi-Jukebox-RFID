import logging
import jukebox.cfghandler
import jukebox.plugs as plugin
import components.rfid.reader

logger = logging.getLogger('jb.sync_shared')

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

        components.rfid.reader.rfid_card_detect_callbacks.register(rfid_card_detect_callback)

def syncCardDatabase():
    logger.debug("Sync Database.")


def rfid_card_detect_callback(card_id: str, state: int):
    logger.debug("RFID Scan Callback.")
    if (state != 0):
        logger.debug("Unkown CardId. No syncing")
    else:
        logger.debug(f"CardId {card_id}. syncing")

