import evdev
import select
import logging
from typing import (
    List)
# overload,
# cast,
# Callable,
# Type,
# Dict,
# Mapping,
# Iterable,
# Optional,
# Union,
# Any

import misc.inputminus as pyil
from misc.simplecolors import Colors
from components.rfid import ReaderBaseClass
import jukebox.cfghandler

from .description import DESCRIPTION

# Create logger
logger = logging.getLogger('jb.rfid.usb')
cfg = jukebox.cfghandler.get_handler('rfid')


def _get_devices() -> List[evdev.InputDevice]:
    """
    Open all input devices for inspection
    :return: List of input devices
    """
    return [evdev.InputDevice(fn) for fn in evdev.list_devices()]


def _close_devices(device_list) -> None:
    """
    Close listed input devices
    :param device_list: List of opened input devices to be closed
    :return: None
    """
    for d in device_list:
        d.close()


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

    try:
        device_key_list = device.capabilities()[evdev.ecodes.EV_KEY]
        is_keyboard_res = mandatory_keys.issubset(device_key_list) and reserved_key.isdisjoint(device_key_list)
    except KeyError:
        is_keyboard_res = False
    logger.debug(f"is_keyboard test for '{device.name}' at '{device.path}' is '{is_keyboard_res}'")
    return is_keyboard_res


def query_customization() -> dict:
    print("\nChoose RFID device from USB device list:\n"
          "If you are planning to connect multiple USB Readers make sure ALL of them are connected before running this script!"
          f"If your RFID reader appears multiple times ({Colors.lightgreen}e.g. KKMoon{Colors.reset}), "
          f"select the one which has {Colors.lightgreen}PASS{Colors.reset} in the isKey column.\n"
          f"For the curious: isKey indicates a device capability check for required keys")
    devices = _get_devices()
    logger.debug(f"USB devices: {[x.name for x in devices]}")
    devices_is_key = [_is_keyboard(x) for x in devices]
    print(f" {Colors.lightgreen}ID{Colors.reset}: "
          f"{Colors.lightgreen}isKey{Colors.reset}: {Colors.lightcyan}Name{Colors.reset}")
    if len(devices) == 0:
        logger.error("USB device list is empty. Make sure USB RFID reader is connected. Then re-run reader registration")
        return {'device_name': '__error_empty_device_list__'}
    for idx, (dev, key) in enumerate(zip(devices, devices_is_key)):
        print(f" {Colors.lightgreen}{idx:2d}{Colors.reset}:"
              f" {Colors.lightgreen}{'PASS' if key else '    '}{Colors.reset} : "
              f"{Colors.lightcyan}{Colors.bold}{dev.name:20}{Colors.reset}")
        print(f"              {Colors.lightgrey}({dev.phys} // {dev.info}{Colors.reset})")
    print("")
    dev_id = pyil.input_int("Device number?", min=0, max=len(devices) - 1, prompt_color=Colors.lightgreen, prompt_hint=True)

    # dev.name is not unique in case
    #   (a) the multiple identical devices are connected
    #   (b) a device registers itself multiple times with different capabilities (e.g. KKMoon)
    # dev.phys is unique down to the actual USB port used
    #   i.e. if the device gets unplugged and re-plugged into a different USB port it will not be recognized again
    # The solution is to use as little information as possible to identify the USB Reader
    #   Pro: It does not matter which USB port is used, or if a USB hub is later inserted
    #   Con: All RFID readers must be connected BEFORE running the query_customization, so we can identify possible duplicates
    # "As little information as possible" means
    #   (a) check if name is unique
    #   (b) check if name + isKey is unique
    #   (c) use full physical path
    name_is_unique = len([d for d in devices if d.name == devices[dev_id].name]) == 1
    key_check_is_unique = len([d for x, d in enumerate(devices)
                              if d.name == devices[dev_id].name and devices_is_key[x] == devices_is_key[dev_id]]) == 1

    _close_devices(devices)

    return {'device_name': devices[dev_id].name,
            'device_phys': devices[dev_id].phys,
            'key_check': devices_is_key[dev_id],
            'name_is_unique': name_is_unique,
            'key_check_is_unique': key_check_is_unique,
            'log_all_keys': False}


class ReaderClass(ReaderBaseClass):
    def __init__(self, reader_cfg_key, logger=None):
        self._logger = logger
        if logger is None:
            self._logger = logging.getLogger(f'jb.rfid.usb({reader_cfg_key})')
        super().__init__(reader_cfg_key=reader_cfg_key, description=DESCRIPTION, logger=self._logger)

        # Key event codes return from evdev are numerical indexes, not decoded ASCII characters
        # Use a string to index with key event code to decode key event code into ASCII character
        self.keys = "X^1234567890XXXXqwertzuiopXXXXasdfghjklXXXXXyxcvbnmXXXXXXXXXXXXXXXXXXXXXXX"

        with cfg:
            config = cfg.getn('rfid', 'readers', reader_cfg_key, 'config', default=None)
            if config is None:
                self._logger.error("Configuration may not be empty!!")
                raise KeyError("configuration may not be empty!!")

            if 'device_name' not in config:
                self._logger.error("Mandatory key 'device_name' not given in configuration!")
                raise KeyError("Mandatory key 'device_name' not given in configuration!")
            if 'device_phys' not in config:
                self._logger.warning("Key 'device_phys' not given in configuration! Trying without...")
            if 'name_is_unique' not in config:
                self._logger.warning("Key 'name_is_unique' not given in configuration! Using default value: 'true'.")
            if 'key_check_is_unique' not in config:
                self._logger.warning("Key 'key_check_is_unique' not given in configuration! Using default value: 'true'.")

            device_name = config.get('device_name')
            device_phys = config.setdefault('device_phys', default='Empty')
            key_check = config.setdefault('key_check', default=True)
            name_is_unique = config.setdefault('name_is_unique', default=True)
            key_check_is_unique = config.setdefault('key_check_is_unique', default=True)
            self.log_all_keys = config.setdefault('log_all_keys', default=False)

        device_list = _get_devices()
        self._logger.debug(f"Device list = {device_list}")
        for idx, device in enumerate(device_list):
            self._logger.debug(f"Inspecting device '{device.name}' at '{device}'")
            # See comment in 'query_customization()' for this decision tree
            if device.name == device_name and (name_is_unique or (key_check == _is_keyboard(device)
                                                                  and (key_check_is_unique or device.phys == device_phys))):
                self._logger.info(f"Device found. Opening device '{device.name}' at '{device}'")
                self.dev = device
                dev_idx = idx
                break
        else:
            _close_devices(device_list)
            self._logger.error(f"Could not find the device '{device_name}' ({device_phys}). Make sure it is connected.")
            raise FileNotFoundError(f"Could not find the device '{device_name}' ({device_phys}). Make sure it is connected.")

        device_list.pop(dev_idx)
        _close_devices(device_list)
        self._keep_running = True

    def cleanup(self):
        if self._keep_running is True:
            self._logger.error("_keep_running True, while closing down. Forgot to call stop() first?")
        self.dev.close()

    def stop(self):
        self._keep_running = False

    def read_card(self) -> str:
        card_uid = ''
        key = ''
        while self._keep_running:
            r, w, x = select.select([self.dev], [], [], 0.2)
            try:
                for event in self.dev.read():
                    if event.type == evdev.ecodes.EV_KEY and event.value == evdev.events.KeyEvent.key_down:
                        key = evdev.ecodes.KEY[event.code]
                        try:
                            char = self.keys[event.code]
                        except IndexError:
                            self._logger.error("Ignoring received a key outside my valid range: "
                                               f"key index = {event.code} --> {key}")
                            char = 'X'
                        card_uid += char

                        if self.log_all_keys:
                            # This debug output uses a print rather than a self._logger,
                            # as it only appends a single char at a time
                            print(char,
                                  end='' if key != 'KEY_ENTER' else '\n',
                                  flush=True)

                    if key == 'KEY_ENTER':
                        return card_uid[:-1]

            except BlockingIOError:
                pass

        self._logger.debug(f"Raising StopIteration with keep_running = {self._keep_running}")
        raise StopIteration
