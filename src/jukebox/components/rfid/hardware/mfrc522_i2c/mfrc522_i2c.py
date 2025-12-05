import logging

import jukebox.cfghandler
from mfrc522_i2c import MFRC522

from ...readerbase import ReaderBaseClass

from .description import DESCRIPTION


cfg = jukebox.cfghandler.get_handler("rfid")


def query_customization() -> dict:
    print(
        "RFID MFRC522 (I2C) default parameters should work unless you changed the address."
    )
    return {"i2c_bus": 1, "i2c_address": 0x28, "log_all_cards": False}


class ReaderClass(ReaderBaseClass):
    def __init__(self, reader_cfg_key):
        self._logger = logging.getLogger(f"jb.rfid.522i2c({reader_cfg_key})")
        super().__init__(
            reader_cfg_key=reader_cfg_key, description=DESCRIPTION, logger=self._logger
        )

        with cfg:
            config = cfg.setndefault(
                "rfid", "readers", reader_cfg_key, "config", value={}
            )
            self.i2c_bus = config.setdefault("i2c_bus", 1)
            self.i2c_address = config.setdefault("i2c_address", 0x28)
            self.log_all_cards = config.setdefault("log_all_cards", False)

        self._keep_running = True
        self._identified_card = False

        # Create instance of MFRC522 (I2C)
        self.device = MFRC522(self.i2c_bus, self.i2c_address)

        # Print version for debug
        self._logger.info(f"MFRC522(I2C) version: {self.device.getReaderVersion()}")

    def cleanup(self):
        del self.device

    def stop(self):
        self._keep_running = False

    def _uid_to_string(self, uid):
        uid_str = ""
        for uid_section in uid:
            uid_str += f"{uid_section:02x}"
        return uid_str

    def read_card(self) -> str:
        if not self._keep_running:
            return ""

        # Only try to detect a card if we previously failed to identify one.
        if not self._identified_card:
            status, _, _ = self.device.scan()
            if status != self.device.MIFARE_OK:
                return ""

        # Identify the card (will fail if no card is present)
        status, uid, _ = self.device.identify()
        if status == self.device.MIFARE_OK:
            uid_str = self._uid_to_string(uid)

            if self.log_all_cards:
                self._logger.debug(f"Card detected with ID = {uid_str}")

            self._identified_card = True
            return uid_str
        else:
            self._identified_card = False
            return ""
