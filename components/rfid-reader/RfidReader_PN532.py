#!/usr/bin/env python3
# This alternative Reader.py script was meant to cover not only USB readers but more.
# It can be used to replace Reader.py if you have readers such as
# MFRC522, RDM6300 or PN532.
# Please use the github issue threads to share bugs and improvements
# or create pull requests.
import logging

logger = logging.getLogger(__name__)

class Pn532Reader:
    def __init__(self):
        from py532lib.i2c import Pn532_i2c
        from py532lib.mifare import Mifare
        pn532 = Pn532_i2c()
        self.device = Mifare()
        self.device.SAMconfigure()
        self.device.set_max_retries(MIFARE_WAIT_FOR_ENTRY)

    def readCard(self):
        return str(+int('0x' + self.device.scan_field().hex(), 0))

    def cleanup(self):
        # Not sure if something needs to be done here.
        logger.debug("PN532Reader clean up.")