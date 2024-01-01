# Standard imports from python packages
import logging

import nfc
from nfc.clf import RemoteTarget

# Import the ReaderBaseClass for common API. Leave as this line as it is!
from components.rfid import ReaderBaseClass
import jukebox.cfghandler

# Also import the description string into this module, to make everything available in a single module w/o code duplication
# Leave this line as is!
from .description import DESCRIPTION

# Create logger.
# Logging is fully setup. Just replace '.new' with something meaningful and short
logger = logging.getLogger('jb.rfid.new')
# Get the global handler to the RFID config
cfg = jukebox.cfghandler.get_handler('rfid')




def query_customization() -> dict:
    """
    Query the user for reader parameter customization
    """
    return {}


class ReaderClass(ReaderBaseClass):
    """
    The reader class for nfcpy supported NFC card readers.
    """
    def __init__(self, reader_cfg_key):
        # Create a per-instance logger, just in case the reader will run multiple times in various threads
        # Replace '.new' with something meaningful and short
        self._logger = logging.getLogger(f'jb.rfid.new({reader_cfg_key})')
        # Initialize the super-class. Don't change anything here
        super().__init__(reader_cfg_key=reader_cfg_key, description=DESCRIPTION, logger=self._logger)

        # Get the configuration from the rfid.yaml:
        # Lock config around the access
        #with cfg:
        #    # Get a reference to the actual reader-specific config
        #    config = cfg.getn('rfid', 'readers', reader_cfg_key, 'config', default=None)
        #    # No config

        self.clf = nfc.ContactlessFrontend('usb')

        self._keep_running = True

    def cleanup(self):
        """
        The cleanup function: free and release all resources used by this card reader (if any).
        """
        self.clf.close()

    def stop(self):
        """
        This function is called to tell the reader to exit its reading function.
        """
        self._keep_running = False

    def read_card(self) -> str:
        """
        Blocking or non-blocking function that waits for a new card to appear and return the card's UID as string
        """
        self._logger.debug("Wait for card")
        while self._keep_running:
            target = self.clf.sense(RemoteTarget('106A'),
                                    RemoteTarget('106B'),
                                    RemoteTarget('212F'),
                                    interval=0.1,
                                    iterations=1)
            if not target:
                continue

            tag = nfc.tag.activate(self.clf, target)
            if not tag:
                continue

            id = ''
            for char in tag.identifier:
                id += '%02X' % char

            self._logger.debug(f'Found card with ID: "{id}"')
            return id
        self._logger.debug("NFC read stopped")
        return ''
