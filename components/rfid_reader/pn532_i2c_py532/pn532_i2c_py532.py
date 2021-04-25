import logging
import configparser

from py532lib.mifare import Mifare
from py532lib.mifare import MIFARE_WAIT_FOR_ENTRY

from base.readerbase import *

from .description import DESCRIPTION


logger = logging.getLogger(os.path.basename(__file__).ljust(25))
logger.setLevel(logging.DEBUG)
logconsole = logging.StreamHandler()
logconsole.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)-8s: %(message)s', datefmt='%d.%m.%Y %H:%M:%S'))
logconsole.setLevel(logging.INFO)
logger.addHandler(logconsole)


def query_customization() -> dict:
    print("There are no customization parameters necessary!")
    return {'log_all_cards': 'false'}


class ReaderClass(ReaderBaseClass):
    def __init__(self, params: dict):
        super().__init__(description=DESCRIPTION, params=params, logger=logger)
        config = configparser.ConfigParser()
        config.read_dict({'params': params})
        self.log_all_cards = config['params'].getboolean('log_all_cards', fallback=False)

        self.device = Mifare()
        self.device.SAMconfigure()
        self.device.set_max_retries(MIFARE_WAIT_FOR_ENTRY)

    def cleanup(self):
        self.device.PN532.close()
        del self.device

    def read_card(self) -> str:
        # scan_field returns a byte array -> convert to true integer
        byte_uid = self.device.scan_field()
        try:
            card_uid = str(int(byte_uid.hex(), base=16))
        except ValueError as e:
            logger.debug(f"Error while reading card. Raw card ID = {byte_uid}")
            return ''

        if self.log_all_cards:
            logger.debug(f"Card detected with ID = {card_uid}")

        return card_uid



