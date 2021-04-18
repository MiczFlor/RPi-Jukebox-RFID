import evdev
import select
import os
import logging
import configparser

import base.inputminus as pyil
from base.simplecolors import colors
from base.readerbase import *

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

    Some RFID readers (e.g. KKMoon) and keyboards appear multiple times in the device list with identical names.
    To differentiate between them, a look at the device capabilities is necessary.
    One device has normal keyboard keys (this is what we want), the other has only specialized keys.

    :parameter device: an opened evdev.InputDevice to inspect
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
          f"select the one which has {colors.red}PASS{colors.reset} in the isKey column.\n"
          f"For the curious: isKey indicates a device capability check for required keys")
    devices = _get_devices()
    logger.debug(f"USB devices: {[x.name for x in devices]}")
    devices_is_key = [_is_keyboard(x) for x in devices]
    print(f" {colors.lightgreen}ID{colors.reset}: {colors.red}isKey{colors.reset}: {colors.lightcyan}Name{colors.reset}")
    if len(devices) == 0:
        logger.error("USB device list is empty. Make sure USB RFID reader is connected. Then re-run register_reader.py")
        return {'device_name': '__error_empty_device_list__'}
    for idx, (dev, key) in enumerate(zip(devices, devices_is_key)):
        print(f" {colors.lightgreen}{idx:2d}{colors.reset}:"
              f" {colors.red}{'PASS' if key else '    '}{colors.reset} : "
              f"{colors.lightcyan}{colors.bold}{dev.name:20}{colors.reset}")
        print(f"              {colors.lightgrey}({dev.phys} // {dev.info}{colors.reset})")
    print("")
    dev_id = pyil.input_int("Device number?", min=0, max=len(devices)-1, prompt_color=colors.lightgreen, prompt_hint=True)

    # USB input device is identified by dev.name and dev.phys. This should be unique (hopefully) but is not guaranteed
    # In case it is not, we may still perform the is_keyboard check when initializing the reader and pick the device with the right keys.
    # Note: I don't think this is necessary, when using name + pyhs for device identification.
    # But you never know what is our there in the wild!
    # Just in case those two values are ambiguous, lets turn on the keyboard check on reader initialization, as that is the
    # the tried and proven code for KKMoon. But to avoid confusion and complexity, only do this when the device is not unique
    key_check = False
    if len([x for x in devices if x.name == devices[dev_id].name and x.phys == devices[dev_id].phys]) > 1:
        print("\nUSB device disambiguation by key capability check on device required:\n"
              f"Your selected RFID reader appears in the device list twice. This can happen with {colors.red}e.g. KKMoon{colors.reset}.\n"
              "For these readers a key capability check must be activated to automatically select the correct USB device.\n")
        key_check = pyil.input_yesno("Enable key capability check?", blank=True, prompt_color=colors.lightgreen, prompt_hint=True)

    return {'device_name': devices[dev_id].name,
            'device_phys': devices[dev_id].phys,
            'key_capability_check': key_check,
            'log_all_keys': 'false'}


class ReaderClass(ReaderBaseClass):
    def __init__(self, params: dict):
        super().__init__(description=DESCRIPTION, params=params, logger=logger)

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
        if 'device_phys' not in config['params']:
            logger.error(f"Mandatory key 'device_phys' not given in dictionary params!")
            raise KeyError(f"Mandatory key 'device_phys' not given in dictionary params!")
        if 'key_capability_check' not in config['params']:
            logger.warning(f"Key 'key_capability_check' not given in dictionary params! Using default value: 'false'.")
        device_name = config['params'].get('device_name')
        device_phys = config['params'].get('device_phys')
        key_check = config['params'].getboolean('key_capability_check', fallback=False)
        self.log_all_keys = config['params'].getboolean('log_all_keys', fallback=False)

        device_list = _get_devices()
        logger.debug(f"Device list = {device_list}")
        for device in device_list:
            logger.debug(f"Inspecting device '{device.name}' at '{device}'")
            if device.name == device_name and device.phys == device_phys and (not key_check or _is_keyboard(device)):
                logger.info(f"Device found. Opening device '{device.name}' at '{device}'")
                self.dev = device
                break
        else:
            logger.error(f"Could not find the device '{device_name}' ({device_phys}). Make sure it is connected.")
            raise FileNotFoundError(f"Could not find the device '{device_name}' ({device_phys}). Make sure it is connected.")

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
