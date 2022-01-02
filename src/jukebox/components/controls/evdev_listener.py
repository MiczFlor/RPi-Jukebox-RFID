import logging
import threading
import time
import traceback

import evdev as ev
import select

import jukebox.cfghandler
import jukebox.publishing
from typing import (Dict, Callable, Optional, Set)

logger = logging.getLogger('jb.evdev')
cfg = jukebox.cfghandler.get_handler('jukebox')


def _filter_by_mandatory_keys(all_devices, mandatory_keys: Set[int]):
    for dev in all_devices:
        try:
            device_key_list = dev.capabilities()[ev.ecodes.EV_KEY]
            is_keyboard_res = mandatory_keys.issubset(device_key_list)
        except KeyError:
            is_keyboard_res = False
        if is_keyboard_res:
            yield dev


def _filter_by_device_name(all_devices, device_name: str, exact_name: bool = True):
    return filter(lambda dev: (dev.name == device_name and exact_name) or (device_name in dev.name and not exact_name),
                  all_devices)


def find_device(device_name: str, exact_name: bool = True, mandatory_keys: Optional[Set[int]] = None) -> str:
    if mandatory_keys is None:
        mandatory_keys = set()

    all_devices = [ev.InputDevice(path) for path in ev.list_devices()]
    named_devices = list(_filter_by_device_name(all_devices, device_name, exact_name))
    capable_devices = list(_filter_by_mandatory_keys(named_devices, mandatory_keys))

    if len(capable_devices) == 0:
        if len(list(named_devices)) > 0:
            raise AttributeError(f"Device '{device_name}' found but w/o mandatory keys: "
                                 f"{ev.resolve_ecodes(ev.ecodes.KEY, mandatory_keys)}")
        else:
            raise FileNotFoundError(f"Cannot find device {device_name} (exact_name = {exact_name})")
    else:
        if len(capable_devices) != 1:
            logger.warning(f"Find evdev input device for {device_name} is non-unique: {capable_devices}. "
                           f"Using first device {capable_devices[0].path}")
        device: ev.InputDevice = capable_devices[0]
        device_path = device.path
        logger.debug(f"Evdev search for '{device_name}' yields: {device.name}, {device.phys}, {device_path}")

    for dev in all_devices:
        dev.close()

    return device_path


class EvDevKeyListener(threading.Thread):
    def __init__(self, device_name_request: str, exact_name: bool, thread_name: str):
        super().__init__(name=thread_name, daemon=True)
        self.device: Optional[ev.InputDevice] = None
        self.device_name_request = device_name_request
        self.exact_name = exact_name
        self.mandatory_keys: Set[int] = set()

        self.button_callbacks: Dict[int, Callable] = {}
        self._keep_running: bool = True

        self.open_retry_cnt = 5
        self.open_retry_delay = 0.5
        self.open_initial_delay = 0.0

    def stop(self):
        self._keep_running = False

    def _connect(self):
        self.device = ev.InputDevice(find_device(self.device_name_request, self.exact_name, self.mandatory_keys))

    def _listen(self):
        logger.debug(f"Listening for events from '{self.device.name}'")
        while self._keep_running:
            r, w, x = select.select([self.device], [], [], 0.2)
            try:
                for event in self.device.read():
                    if event.type == ev.ecodes.EV_KEY:
                        # Only act on button press, not button release
                        if event.value == ev.events.KeyEvent.key_down:
                            # Report the button event
                            if logger.isEnabledFor(logging.DEBUG):
                                logger.debug(ev.categorize(event))
                            func = self.button_callbacks.get(event.code, None)
                            if func:
                                try:
                                    func()
                                except Exception as e:
                                    logger.error(f'Error in callback {func.__name__} from button {ev.categorize(event)}\n'
                                                 f'Reason: {e.__class__.__name__}: {e}')
                            else:
                                logger.info(f'No callback registered for button {ev.categorize(event)}')
            except BlockingIOError:
                pass

    def run(self):
        time.sleep(self.open_initial_delay)
        for idx in range(self.open_retry_cnt):
            try:
                self._connect()
            except FileNotFoundError as e:
                # This error occurs, if opening the bluetooth input device fails
                logger.debug(f"{e} (attempt: {idx+1}/{self.open_retry_cnt}). Retrying in {self.open_retry_delay}")
                time.sleep(self.open_retry_delay)
            except AttributeError as e:
                # This error occurs, when the device can be found, but does not have the mandatory keys
                logger.info(f"{e.__class__.__name__}: {e}. Ignoring device.")
                break
            else:
                break
        else:
            logger.info(
                f"Could not open device '{self.device_name_request}' as HID after {self.open_retry_cnt} attempts. Giving up.")

        if self.device:
            try:
                self._listen()
            except OSError:
                # This error occurs, when the already opened bluetooth device suddenly gets disconnected
                logger.info(f"Device disconnected {self.device_name_request}")
            except Exception as e:
                logger.error(f'{e.__class__.__name__}: {e}\n{traceback.format_exc()}')
                if self.device:
                    self.device.close()
            else:
                self.device.close()
        logger.debug(f'Exit thread {self.name}')
