import logging
import threading
import time
import importlib
import functools
import jukebox.plugs as plugs
import jukebox.cfghandler
import jukebox.utils as utils
import jukebox.publishing as publishing

from .button import Button
from .rotary_encoder import RotaryEncoder

log = logging.getLogger('jb.gpio')

cfg_gpio = jukebox.cfghandler.get_handler('gpio')
cfg_main = jukebox.cfghandler.get_handler('jukebox')

gpio = None


class GpioRpiClass(threading.Thread):
    def __init__(self, cfg_gpio):
        self._logger = logging.getLogger('jb.gpio')
        super().__init__(name="GPIO Thread", daemon=True)

        self._cancel = threading.Event()
        self.devices = cfg_gpio['devices']

        self.device_map = {'Button': Button,
                           'RotaryEncoder': None,
                           'RockerButton': None,
                           'PortOut': None}
        self.devicelist = []
        self.portlist = {}
        
        # iterate over all GPIO devices
        for dev in self.devices.keys():
            self.devicelist.append(self.generate_device(self.devices[dev], dev))

    def generate_device(self, device_config, name):
        device_type = device_config['Type']

        device = self.device_map.get(device_type)

        if (device is not None):
            return (device(name, device_config))
        else:
            return None

    def run(self):
        self._logger.debug("Start GPIO Rpi")

        while not self._cancel.is_set():
            pass


@plugs.finalize
def finalize():
    global gpio
    jukebox.cfghandler.load_yaml(cfg_gpio, cfg_main.getn('gpio', 'gpio_rpi_config'))
    gpio = GpioRpiClass(cfg_gpio)
    gpio.start()


@plugs.atexit
def atexit(**ignored_kwargs):
    global gpio
    gpio.stop()
    return None
