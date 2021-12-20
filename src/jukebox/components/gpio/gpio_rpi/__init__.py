import logging
import threading
import jukebox.plugs as plugs
import jukebox.cfghandler
import time

from .button import Button
from .rotary_encoder import RotaryEncoder
from .port_out import PortOut

log = logging.getLogger('jb.gpio')
gpio = None


class GpioRpiClass(threading.Thread):
    def __new__(cls, cfg_gpio):
        failm = "\nGPIO failed to start"
        instance = None

        devices = cfg_gpio.get('devices')

        if cfg_gpio is None:
            log.error(f"No valid configuration found{failm}")
        elif devices is None:
            log.error(f"Section \"devices\" is mandatory in {cfg_gpio._loaded_from}{failm}")
        else:
            instance = super(GpioRpiClass, cls).__new__(cls)
            instance.devices = devices
            instance.config_name = cfg_gpio._loaded_from
        return instance

    def __init__(self, cfg_gpio):
        self._logger = logging.getLogger('jb.gpio')
        super().__init__(name="GPIO Thread", daemon=True)

        self._cancel = threading.Event()
        self.devices = cfg_gpio['devices']

        self.device_map = {'Button': Button,
                           'RotaryEncoder': RotaryEncoder,
                           'RockerButton': None,
                           'PortOut': PortOut}
        self.devicelist = {}

        # iterate over all GPIO devices
        for dev_name in self.devices.keys():
            dev = self.generate_device(self.devices[dev_name], dev_name)
            if dev is not None:
                self.devicelist[dev_name] = dev

    def generate_device(self, device_config, name):
        device_type = device_config['Type']

        device = self.device_map.get(device_type)

        if (device is not None):
            return (device(name, device_config, self.config_name))
        else:
            return None

    @plugs.tag
    def SetPortState(self, name, state):
        port = self.devicelist.get(name)
        if isinstance(port, PortOut):
            port.SetPortState(state)
        else:
            if port is None:
                fm = "not existing"
            else:
                fm = "not a PortOut"
            log.error(f"Could not set Port State, \"{name}\" is {fm} ")
            print(type(port))
        return 0

    @plugs.tag
    def StartPortSequence(self, seq):
        name = seq.get('name')
        port = self.devicelist.get(name)
        if isinstance(port, PortOut):
            port.StartPortSequence(seq)
        else:
            if port is None:
                fm = "not existing"
            else:
                fm = "not a PortOut"
            log.error(f"Could not set Port State, \"{name}\" is {fm} ")
        return (0)

    @plugs.tag
    def StopPortSequence(self, name):
        port = self.devicelist.get(name)
        if isinstance(port, PortOut):
            port.StopPortSequence()
        else:
            if port is None:
                fm = "not existing"
            else:
                fm = "not a PortOut"
            log.error(f"Could not set Port State, \"{name}\" is {fm} ")
        return (0)

    def run(self):
        self._logger.debug("Start GPIO Rpi")
        self._cancel.wait()
        self._logger.debug("Stopped GPIO Rpi")

    def stop(self):
        self._logger.debug("Stopping GPIO Rpi")
        for dev in self.devicelist:
            self.devicelist[dev].stop()
        time.sleep(0.2)
        self._cancel.set()


@plugs.finalize
def finalize():
    global gpio
    cfg_gpio = jukebox.cfghandler.get_handler('gpio')
    cfg_main = jukebox.cfghandler.get_handler('jukebox')
    jukebox.cfghandler.load_yaml(cfg_gpio, cfg_main.getn('gpio', 'gpio_rpi_config'))
    gpio = GpioRpiClass(cfg_gpio)
    if gpio is not None:
        plugs.register(gpio, name='gpio')
        gpio.start()


@plugs.atexit
def atexit(**ignored_kwargs):
    global gpio
    if gpio is not None:
        gpio.stop()
    return None
