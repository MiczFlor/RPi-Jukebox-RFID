# Standard imports from python packages
import logging

import nfc
import glob
from nfc.clf import RemoteTarget

# Import the ReaderBaseClass for common API. Leave as this line as it is!
from components.rfid import ReaderBaseClass
import jukebox.cfghandler
import misc.inputminus as pyil
from misc.simplecolors import Colors

# Also import the description string into this module, to make everything available in a single module w/o code duplication
# Leave this line as is!
from .description import DESCRIPTION

# Create logger.
logger = logging.getLogger('jb.rfid.nfcpy')
# Get the global handler to the RFID config
cfg = jukebox.cfghandler.get_handler('rfid')


def query_customization() -> dict:
    possible_device_ids = [
        "usb:054c:02e1",
        "usb:054c:06c1",
        "usb:054c:06c3",
        "usb:054c:0193",
        "usb:04cc:0531",
        "usb:072f:2200",
        "usb:04e6:5591",
        "usb:04e6:5593",
        "usb:04cc:2533",
    ]

    devices = []
    clf = nfc.ContactlessFrontend()

    # find usb devices
    for device_id in possible_device_ids:
        if clf.open(device_id):
            devices.append({'id': device_id, 'vendor': clf.device.vendor_name, 'name': clf.device.product_name})
            clf.close()

    # find tty device
    matching_files = glob.glob("/dev/ttyUSB[0-9]*")
    matching_files += glob.glob("/dev/ttyACM[0-9]*")
    for file_path in matching_files:
        for device_id in (f'{file_path}:pn532', f'{file_path}:arygon'):
            if clf.open(device_id):
                devices.append({'id': device_id, 'vendor': clf.device.vendor_name, 'name': clf.device.product_name})
                clf.close()

    print("\nChoose RFID device from USB device list:\n")
    logger.debug(f"USB devices: {[x['name'] for x in devices]}")
    if len(devices) == 0:
        logger.error("USB device list is empty. Make sure USB RFID reader is connected. Then re-run register_reader.py")
        return {'device_path': None}

    for idx, dev in enumerate(devices):
        print(f" {Colors.lightgreen}{idx:2d}{Colors.reset}:"
              f"{Colors.lightcyan}{Colors.bold}{dev['vendor']} {dev['name']}{Colors.reset}")

    dev_id = pyil.input_int("Device number?", min=0, max=len(devices) - 1, prompt_color=Colors.lightgreen, prompt_hint=True)
    device_path = devices[dev_id]['id']

    return {'device_path': device_path}


class ReaderClass(ReaderBaseClass):
    """
    The reader class for nfcpy supported NFC card readers.
    """
    def __init__(self, reader_cfg_key):
        # Create a per-instance logger, just in case the reader will run multiple times in various threads
        self._logger = logging.getLogger(f'jb.rfid.nfcpy({reader_cfg_key})')
        # Initialize the super-class. Don't change anything here
        super().__init__(reader_cfg_key=reader_cfg_key, description=DESCRIPTION, logger=self._logger)

        # Get the configuration from the rfid.yaml:
        # Lock config around the access
        with cfg:
            # Get a reference to the actual reader-specific config
            config = cfg.getn('rfid', 'readers', reader_cfg_key, 'config', default=None)

        device_path = config.setdefault('device_path', None)
        self.clf = nfc.ContactlessFrontend()
        self.clf.open(device_path)

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
