import logging

import jukebox.cfghandler

logger = logging.getLogger('jb.synchronisation.sync_shared')
cfg_cards = jukebox.cfghandler.get_handler('cards')


def syncCardDatabase():
    logger("Sync Database.")


def rfid_card_detect_callback(card_id: str, state: int):
    logger("RFID Scan Callback.")
    if (state != 0):
        logger("Unkown CardId. No syncing")
    else:
        logger(f"CardId {card_id}. syncing")
