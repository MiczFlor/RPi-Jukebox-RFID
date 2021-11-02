import logging
import threading
import jukebox.plugs as plugs
import jukebox.cfghandler

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
                           'RotaryEncoder': RotaryEncoder,
                           'RockerButton': None,
                           'PortOut': None}
        self.devicelist = []
        self.portlist = {}

        # iterate over all GPIO devices
        for dev_name in self.devices.keys():
            dev = self.generate_device(self.devices[dev_name], dev_name)
            if dev is not None:
                self.devicelist.append(dev)

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

    def stop(self):
        self._logger.debug("Stopping GPIO Rpi")
        self._cancel.set()

        for dev in self.devicelist:
            dev.stop()


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
