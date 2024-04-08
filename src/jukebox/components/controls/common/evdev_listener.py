"""
Generalized listener for ``dev/input`` devices
"""
import logging
import threading
import time
import traceback

import evdev
import evdev as ev
import select

import jukebox.cfghandler
import jukebox.publishing
from typing import (Dict, Callable, Optional, Set, List, Iterable)

logger = logging.getLogger('jb.evdev')
cfg = jukebox.cfghandler.get_handler('jukebox')


def _filter_by_mandatory_keys(all_devices: List[evdev.InputDevice], mandatory_keys: Set[int]) -> Iterable[evdev.InputDevice]:
    """Generator filtering all_devices based on mandatory keys

    :param all_devices: List of input device candidates
    :param mandatory_keys: Set of integer key codes that included devices must have"""
    for dev in all_devices:
        try:
            device_key_list = dev.capabilities()[ev.ecodes.EV_KEY]
            is_keyboard_res = mandatory_keys.issubset(device_key_list)
        except KeyError:
            is_keyboard_res = False
        if is_keyboard_res:
            yield dev


def _filter_by_device_name(all_devices: List[evdev.InputDevice],
                           device_name: str, exact_name: bool = True) -> Iterable[evdev.InputDevice]:
    """Generator filtering all_devices based on device_name

    :param all_devices: List of input device candidates
    :param device_name: The device name to look for
    :param exact_name: If true, device_name must mach exactly, else a match is returned if device_name is a substring of
        the reported device name
    """
    return filter(lambda dev: (dev.name == device_name and exact_name) or (device_name in dev.name and not exact_name),
                  all_devices)


def find_device(device_name: str, exact_name: bool = True, mandatory_keys: Optional[Set[int]] = None) -> str:
    """Find an input device with device_name and mandatory keys.

    :raise FileNotFoundError: if no device is found.
    :raise AttributeError: if device does not have the mandatory key

    If multiple devices match, the first match is returned

    :param device_name: See :func:`_filter_by_device_name`
    :param exact_name: See :func:`_filter_by_device_name`
    :param mandatory_keys: See :func:`_filter_by_mandatory_keys`
    :return: The path to the device
    """
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
    """Opens and event input device from ``/dev/inputs``, and runs callbacks upon the button presses.
    Input devices could be .e.g. Keyboard, Bluetooth audio buttons, USB buttons

    Runs as a separate thread. When device disconnects or disappears, thread exists. A new thread must be started
    when device re-connects.

    Assign callbacks to :attr:`EvDevKeyListener.button_callbacks`
    """
    def __init__(self, device_name_request: str, exact_name: bool, thread_name: str):
        """
        :param device_name_request: The device name to look for
        :param exact_name: If true, device_name must mach exactly, else a match is returned if device_name is a substring of
            the reported device name
        :param thread_name: Name of the listener thread
        """
        super().__init__(name=thread_name, daemon=True)
        self.device: Optional[ev.InputDevice] = None
        self.device_name_request = device_name_request
        self.exact_name = exact_name
        self._keep_running: bool = True

        #: Mandatory keys: see :func:`_filter_by_mandatory_keys`
        self.mandatory_keys: Set[int] = set()

        #: Dict of ``{keycode: Callable}`` where callable is the function to run on the press of keycode
        self.button_callbacks: Dict[int, Callable] = {}

        #: Wait N seconds before trying to open the device.
        #: Can be useful if device open is triggered on a callback, but the system is not ready yet.
        self.open_initial_delay = 0.0
        #: Attempt to open the device N times. In case device is not quite ready when this thread is started.
        self.open_retry_cnt = 5
        #: Delay in seconds between retries
        self.open_retry_delay = 0.5

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
        """"""
        time.sleep(self.open_initial_delay)
        for idx in range(self.open_retry_cnt):
            try:
                self._connect()
            except FileNotFoundError as e:
                # This error occurs, if opening the bluetooth input device fails
                logger.debug(f"{e} (attempt: {idx + 1}/{self.open_retry_cnt}). Retrying in {self.open_retry_delay}")
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

    def start(self) -> None:
        """Start the tread and start listening"""
        super().start()
