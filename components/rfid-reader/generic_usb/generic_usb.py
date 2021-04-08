import evdev
import select
import os
import logging
import configparser

import misc.inputminus as pyil
from misc.simplecolors import colors

from .description import DESCRIPTION

# Create logger
logger = logging.getLogger(os.path.basename(__file__).ljust(25))
logger.setLevel(logging.DEBUG)
# Create console handler and set default level
logconsole = logging.StreamHandler()
logconsole.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)-8s: %(message)s', datefmt='%d.%m.%Y %H:%M:%S'))
logconsole.setLevel(logging.INFO)
logger.addHandler(logconsole)


def _get_devices():
    return [evdev.InputDevice(fn) for fn in evdev.list_devices()]


def _is_keyboard(device: evdev.InputDevice) -> bool:
    """Check if an input device has the keys that are required by a 'normal' keyboard

    Some RFID readers (e.g. KKMoon) and keyboards appear multiple times in the device list with identical name.
    To differentiate between them, a look at the device capabilities is necessary.
    One device has normal keyboard keys (this is what we want), the other has only specialized keys.

    :parameter device: an openpend evdev.InputDevice to inspect
    :return: True/False"""
    # The mandatory keys that the device must have to pass as keyboard
    # Developer note: The range KEY_ESC ... KEY_D has been carried over from the previous implementation
    # for the KKMoon Reader, which is known to work. This range includes also keys such as backspace, right brace, ..
    # Strictly speaking this could probably be restricted, in case it causes problems with new, yet unknown, readers.
    mandatory_keys = {i for i in range(evdev.ecodes.KEY_ESC, evdev.ecodes.KEY_D)}
    # The exclusion keys that the device must NOT have
    reserved_key = {0}

    device_key_list = device.capabilities()[evdev.ecodes.EV_KEY]
    is_keyboard_res = mandatory_keys.issubset(device_key_list) and reserved_key.isdisjoint(device_key_list)
    logger.debug(f"is_keyboard test for '{device.name}' at '{device.fn}' is '{is_keyboard_res}'")
    return is_keyboard_res


def query_customization():
    print("\nChoose RFID device from USB device list:\n"
          f"If your RFID reader appears multiple times ({colors.red}e.g. KKMoon{colors.reset}), "
          "select one of the ambiguous entries. We will take care of that in the next step.\n")
    devices = _get_devices()
    logger.debug(f"USB devices: {[x.name for x in devices]}")
    if len(devices) == 0:
        logger.error("USB device list is empty. Make sure USB RFID reader is connected. Then re-run register_reader.py")
        return {'device_name': '__error_empty_device_list__'}
    for idx, val in enumerate(devices):
        print(f" {colors.lightgreen}{idx:2d}{colors.reset}: {colors.lightcyan}{colors.bold}{val.name}{colors.reset}")
    print("")
    dev_id = pyil.input_int("Device number?", min=0, max=len(devices)-1, prompt_color=colors.lightgreen, prompt_hint=True)

    # Note: The following must only be enabled when the device name is ambiguous. In all other cases, it should do no harm
    # but we will rather stick with the tried and proven code and only enable it for KKMoon and the likes.
    key_check = False
    if len([x for x in devices if x.name == devices[dev_id].name]) > 1:
        print("\nUSB device disambiguation by key capability check on device required:\n"
              f"Your selected RFID reader appears in the device list twice. This is the case with {colors.red}e.g. KKMoon{colors.reset}.\n"
              "For these readers a key capability check must be activated to automatically select the correct USB device.\n")
        key_check = pyil.input_yesno("Enable key capability check?", blank=True, prompt_color=colors.lightgreen, prompt_hint=True)

    return {'device_name': devices[dev_id].name,
            'key_capability_check': key_check,
            'log_all_keys': 'false'}


class Reader:
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        logger.debug(f"Cleaning up behind reader '{DESCRIPTION}'")
        self.cleanup()

    def __init__(self, params: dict):
        logger.debug(f"Initializing reader {DESCRIPTION} from {__file__}")
        logger.debug(f"Parameters = {params}")

        # Key event codes return from evdev are numerical indexes, not decoded ASCII characters
        # Use a string to index with key event code to decode key event codeinto ASCII character
        self.keys = "X^1234567890XXXXqwertzuiopXXXXasdfghjklXXXXXyxcvbnmXXXXXXXXXXXXXXXXXXXXXXX"

        if not params:
            logger.error("Params dictionary may not be empty! Missing mandatory parameters!")
            raise KeyError("Params dictionary may not be empty! Missing mandatory parameters!")

        config = configparser.ConfigParser()
        config.read_dict({'params': params})

        if 'device_name' not in config['params']:
            logger.error(f"Mandatory key 'device_name' not given in dictionary params!")
            raise KeyError(f"Mandatory key 'device_name' not given in dictionary params!")
        if 'key_capability_check' not in config['params']:
            logger.error(f"Mandatory key 'key_capability_check' not given in dictionary params!")
            raise KeyError(f"Mandatory key 'key_capability_check' not given in dictionary params!")
        device_name = config['params'].get('device_name')
        key_check = config['params'].getboolean('key_capability_check')
        self.log_all_keys = config['params'].getboolean('log_all_keys', fallback=False)

        device_list = _get_devices()
        logger.debug(f"Device list = {device_list}")
        for device in device_list:
            if device.name == device_name and (not key_check or _is_keyboard(device)):
                logger.debug(f"Inspecting device '{device.name}' at '{device}'")
                self.dev = device
                break
        else:
            logger.error(f"Could not find the device '{device_name}'. Make sure is connected.")
            raise FileNotFoundError(f"Could not find the device '{device_name}'. Make sure is connected.")

    def cleanup(self):
        pass

    def read_card(self) -> str:
        card_uid = ''
        key = ''
        while key != 'KEY_ENTER':
            r, w, x = select.select([self.dev], [], [])
            for event in self.dev.read():
                if event.type == evdev.ecodes.EV_KEY and event.value == evdev.events.KeyEvent.key_down:
                    key = evdev.ecodes.KEY[event.code]
                    try:
                        card_uid += self.keys[event.code]
                    except IndexError:
                        logger.error(f"Ignoring received a key outside my valid range: key index = {event.code} --> {key}")
                        card_uid += 'X'
                    if self.log_all_keys:
                        # This debug output uses a print rather than a logger, as it only appends a single char at a time
                        print(self.keys[event.code],
                              end='' if key != 'KEY_ENTER' else '\n',
                              flush=True)
        return card_uid[:-1]
