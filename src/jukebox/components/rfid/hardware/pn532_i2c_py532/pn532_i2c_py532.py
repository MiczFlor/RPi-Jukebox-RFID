import logging

from py532lib.mifare import Mifare
from py532lib.mifare import (MIFARE_WAIT_FOR_ENTRY, MIFARE_SAFE_RETRIES)  # noqa: F401

from components.rfid import ReaderBaseClass
import jukebox.cfghandler


from .description import DESCRIPTION


# Create logger
logger = logging.getLogger('jb.rfid.rdm6300')
cfg = jukebox.cfghandler.get_handler('rfid')


def query_customization() -> dict:
    print("There are no customization parameters necessary!")
    return {'log_all_cards': 'false'}


class ReaderClass(ReaderBaseClass):
    def __init__(self, reader_cfg_key):
        self._logger = logging.getLogger(f'jb.rfid.532({reader_cfg_key})')
        super().__init__(reader_cfg_key=reader_cfg_key, description=DESCRIPTION, logger=self._logger)

        self.log_all_cards = cfg.setndefault('rfid', 'readers', reader_cfg_key, 'config', 'log_all_cards', value=False)

        self.device = Mifare()
        self.device.SAMconfigure()
        # self.device.set_max_retries(MIFARE_WAIT_FOR_ENTRY)
        # Let's see how that behaves
        self.device.set_max_retries(MIFARE_SAFE_RETRIES)
        self._keep_running = True

    def cleanup(self):
        self.device.PN532.close()
        del self.device

    def stop(self):
        self._keep_running = False

    def read_card(self) -> str:
        # scan_field returns a byte array -> convert to true integer
        byte_uid = self.device.scan_field()
        if not self._keep_running:
            return ''
        try:
            card_uid = str(int(byte_uid.hex(), base=16))
        except ValueError:
            self._logger.debug(f"Error while reading card. Raw card ID = {byte_uid}")
            return ''

        if self.log_all_cards:
            self._logger.debug(f"Card detected with ID = {card_uid}")

        return card_uid
