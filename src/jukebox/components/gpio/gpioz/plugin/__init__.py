# RPi-Jukebox-RFID Version 3
# Copyright (c) See file LICENSE in project root folder
"""
The GPIOZ plugin interface build all input and output devices from the configuration file and connects
the actions and callbacks. It also provides a very restricted, but common API for the output devices to the RPC.
That API is mainly used for testing. All the relevant output state changes are usually made through callbacks directly
using the output device's API.
"""
import importlib
import logging
import traceback

import gpiozero.pins
from gpiozero.pins.mock import MockFactory, MockPWMPin
import components.gpio.gpioz.core.input_devices
import components.gpio.gpioz.plugin.connectivity

import jukebox.plugs as plugin
import jukebox.cfghandler
import jukebox.publishing
import jukebox.utils
from typing import (Dict, Any, Callable)
import components
import components.volume
import components.rfid.reader
from components.gpio.gpioz.core.mock import patch_mock_outputs_with_callback
from misc import getattr_hierarchical
from jukebox.callingback import CallbackHandler

logger = logging.getLogger('jb.gpioz')
cfg_main = jukebox.cfghandler.get_handler('jukebox')
cfg_gpio = jukebox.cfghandler.get_handler('gpioz')


#: List of all created output devices
output_devices: Dict[str, Any] = {}
#: List of all created input devices
input_devices: Dict[str, Any] = {}

#: The global pin factory used in this module
#: Using different pin factories for different devices is not supported
factory: gpiozero.pins.Factory

#: Indicates that the GPIOZ module is enabled and loaded w/o errors
IS_ENABLED: bool = False
#: Indicates that the pin factory is a mock factory
IS_MOCKED: bool
#: The path of the config file the GPIOZ configuration was loaded from
CONFIG_FILE: str


# ---------------------------------------------------
# Service Running Status Callback
# ---------------------------------------------------
class ServiceIsRunningCallbacks(CallbackHandler):
    """
    Callbacks are executed when

    * Jukebox app started
    * Jukebox shuts down

    This is intended to e.g. signal an LED to change state.
    This is integrated into this module because:

    * we need the GPIO to control a LED (it must be available when the status callback comes)
    * the plugin callback functions provide all the functionality to control the status of the LED
    * which means no need to adapt other modules
    """

    def register(self, func: Callable[[int], None]):
        """
        Add a new callback function :attr:`func`.

        Callback signature is

        .. py:function:: func(status: int)
            :noindex:

        :param status: 1 if app started, 0 if app shuts down
        """
        super().register(func)

    def run_callbacks(self, status: int):
        """:meta private:"""
        super().run_callbacks(status)


#: Callback handler instance for service_is_running_callbacks events.
#: See :class:`ServiceIsRunningCallbacks`
service_is_running_callbacks = ServiceIsRunningCallbacks('service_running_callbacks', logger)


# ---------------------------------------------------
# Pin Factory Creation
# ---------------------------------------------------
# from gpiozero import Device
# from gpiozero.pins.pigpio import PiGPIOFactory
# from gpiozero.pins.rpigpio import RPiGPIOFactory

# https://gpiozero.readthedocs.io/en/stable/remote_gpio.html#pin-factories
# https://gpiozero.readthedocs.io/en/stable/api_pins.html#mock-pins

# factory = RPiGPIOFactory()
# remote_factory = PiGPIOFactory(host='192.168.1.3')
# MockFactory(pin_class=MockPWMPin)

def build_pin_factory():
    global IS_MOCKED
    global factory
    # Supported factories: mock.MockFactory, pigpio.PiGPIOFactory, rpigpio.RPiGPIOFactory
    pin_factory_name: str = cfg_gpio.setndefault('pin_factory', 'type', value='rpigpio.RPiGPIOFactory')
    # Load the modules required for the chosen factory
    # And only those, to avoid problems with missing dependencies and avoid extra load times
    module_name, factory_name = pin_factory_name.rsplit(sep='.', maxsplit=1)
    module = importlib.import_module(f'gpiozero.pins.{module_name}', 'pkg')
    obj = getattr(module, factory_name)
    kwargs = cfg_gpio.getn('pin_factory', pin_factory_name, 'kwargs', default={})
    if issubclass(obj, MockFactory):
        IS_MOCKED = True
        logger.warning("GPIOZ devices are mocked! Not connected to actual hardware!")
        kwargs['pin_class'] = MockPWMPin
        patch_mock_outputs_with_callback()
    factory = obj(**kwargs)


# ---------------------------------------------------
# Output Device Builder
# ---------------------------------------------------

def connect_output_device(device, name, config: Dict):
    connect_func = config.get('connect', None)
    if connect_func is None:
        return
    if isinstance(connect_func, str):
        connect_func = [connect_func]
    for func_name in connect_func:
        try:
            func = getattr_hierarchical(components, func_name)
        except AttributeError as e:
            logger.error(f"Connection function '{func_name}' of '{name}' does not exist: {e.__class__.__name__}: {e}")
            continue
        except Exception as e:
            logger.error(f"In resolving connect function '{func_name}' of '{name}': {e.__class__.__name__}: {e}")
            continue

        try:
            func(device)
        except Exception as e:
            logger.error(f"Error in connection function '{func_name}' for output device '{name}': "
                         f"{e.__class__.__name__}: {e}\n"
                         f"{traceback.format_exc()}")
            continue


def build_output_device(name: str, config: Dict):
    """Construct and register a new output device

    In principal all supported GPIOZero output devices can be used.
    For all devices a custom functions need to be written to control the state of the outputs"""
    global factory
    device_type = config.get('type', None)
    kwargs = config.get('kwargs', {})

    if name in output_devices.keys():
        raise KeyError(f"Output with name '{name}' already exists. Ignoring new configuration.")

    logger.debug(f"Create output device '{name}', type='{device_type}', config={config}")

    if device_type is None:
        raise KeyError(f"Missing mandatory parameter 'type' for device '{name}'.")

    try:
        device_cls = getattr(components.gpio.gpioz.core.output_devices, device_type)
    except AttributeError as e:
        raise AttributeError(f"Unknown device type '{device_type}' for '{name}' ({e})")

    device = device_cls(**kwargs, pin_factory=factory, name=name)
    connect_output_device(device, name, config)
    output_devices[name] = device


def _build_all_output_devices():
    for name, config in cfg_gpio.getn('output_devices', default={}).items():
        try:
            build_output_device(name, config)
        except Exception as e:
            logger.error(f"Error building output device '{name}'. Ignoring this device configuration. "
                         f"Reason: {e.__class__.__name__}: {e}")


# ---------------------------------------------------
# Input Device Builder
# ---------------------------------------------------

def build_input_device(name: str, config):
    """Construct and connect a new input device

    Supported input devices are those from gpio.gpioz.core.input_devices"""
    global factory
    device_type = config.get('type')
    kwargs = config.get('kwargs', {})

    logger.debug(f"Create input device '{name}', type='{device_type}', config={config}")

    try:
        device_cls = getattr(components.gpio.gpioz.core.input_devices, device_type)
    except AttributeError as e:
        logger.error(f"Ignoring unknown device type '{device_type}' (Reason: {e})")
        return

    try:
        device = device_cls(**kwargs, pin_factory=factory, name=name)
    except Exception as e:
        logger.error(f"Error creating input device '{name}' (type={device_type}). Skipping. {e.__class__.__name__}: {e}")
        return
    else:
        device.set_rpc_actions(config.get('actions'))

    input_devices[name] = device


def _build_all_input_devices():
    for name, config in cfg_gpio.getn('input_devices', default={}).items():
        try:
            build_input_device(name, config)
        except Exception as e:
            logger.error(f"Error building input device '{name}': {e.__class__.__name__}: {e}")


# ---------------------------------------------------
# API and RPC function definitions
# ---------------------------------------------------
def get_output(name: str):
    """Get the output device instance based on the configured name

    :param name: The alias name output device instance
    """
    if name not in output_devices.keys():
        raise KeyError(f"No such output device with name '{name}'")
    return output_devices[name]


@plugin.register
def on(name: str):
    """Turn an output device on

    :param name: The alias name output device instance
    """
    get_output(name).on()


@plugin.register
def off(name: str):
    """Turn an output device off

    :param name: The alias name output device instance
    """
    get_output(name).off()


@plugin.register
def set_value(name: str, value: Any):
    """Set the output device to :attr:`value`

    :param name: The alias name output device instance

    :param value: Value to set the device to
    """
    get_output(name).value = value


@plugin.register
def flash(name, on_time=1, off_time=1, n=1, *, fade_in_time=0, fade_out_time=0, tone=None, color=(1, 1, 1)):
    """Flash (blink or beep) an output device

    This is a generic function for all types of output devices. Parameters not applicable to an
    specific output device are silently ignored

    :param name: The alias name output device instance

    :param on_time: Time in seconds in state ``ON``

    :param off_time: Time in seconds in state ``OFF``

    :param n: Number of flash cycles

    :param tone: The tone in to play, e.g. 'A4'. *Only for TonalBuzzer*.

    :param color: The RGB color *only for PWMLED*.

    :param fade_in_time: Time in seconds for transitioning to on. *Only for PWMLED and RGBLED*

    :param fade_out_time: Time in seconds for transitioning to off. *Only for PWMLED and RGBLED*
    """
    get_output(name).flash(on_time=on_time, off_time=off_time, n=n, fade_in_time=fade_in_time, fade_out_time=fade_out_time,
                           tone=tone, color=color)


# ---------------------------------------------------
# GPIOZero output device API
# ---------------------------------------------------
# LED   : on, off, toggle, blink,          value, is_lit
#       : blink(on_time=1, off_time=1, n=None, background=True)
# PWMLED: on, off, toggle, blink, pulse    value, is_lit
#       : blink(on_time=1, off_time=1, fade_in_time=0, fade_out_time=0, n=None, background=True)
#       : pulse(fade_in_time=1, fade_out_time=1, n=None, background=True)
# Buzzer: on, off, toggle, beep,           value, is_active
#       : blink (undocumented)
#       : beep(on_time=1, off_time=1, n=None, background=True)
# TonalBuzzer: play, stop,
# Note that this class does not currently work with PiGPIOFactory (remote pins)

# ---------------------------------------------------
# Plugin registration
# ---------------------------------------------------

@plugin.initialize
def initialize():
    # Boot order:
    # volume.initialize: Config, Start services
    # headphone_buttons.initialize: register callbacks (volume)
    # rfid.initialize: ---
    # gpioz.initialize: create output devices and register their callbacks (e.g. volume, rfid)
    #
    # volume.finalize: set_default output, default volume
    # jingle.finalize: play startup sound
    # headphone_buttons.finalize: --
    # gpioz.finalize: create input devices and bind action calls
    global IS_ENABLED
    global IS_MOCKED
    global CONFIG_FILE
    IS_ENABLED = False
    IS_MOCKED = False
    enable = cfg_main.setndefault('gpioz', 'enable', value=False)
    CONFIG_FILE = cfg_main.setndefault('gpioz', 'config_file', value='../../shared/settings/gpioz.yaml')
    if not enable:
        return
    try:
        jukebox.cfghandler.load_yaml(cfg_gpio, CONFIG_FILE)
    except Exception as e:
        logger.error(f"Disable GPIOZ due to error loading GPIOZ config file. {e.__class__.__name__}: {e}")
        return

    IS_ENABLED = True
    with cfg_gpio:
        build_pin_factory()
        # Build output devices during initialization, such that they
        # can be used (i.e. set) by the other modules during finalization (usually through the registered callbacks)
        _build_all_output_devices()

    logger.debug(f'Completed loading and configuring GPIO output devices (IS_MOCKED={IS_MOCKED})')


@plugin.finalize
def finalize():
    # Build input devices last in finalize,
    # such that all modules are loaded and RPC commands can be de-referenced and bound to endpoint methods
    # to minimize latency on button press
    with cfg_gpio:
        _build_all_input_devices()

    # GPIOZ is one of the last modules loaded, so we can enable the status led here
    # we are so close to operational, that the time difference is not noticeable
    service_is_running_callbacks.run_callbacks(1)


@plugin.atexit
def plugin_atexit(**ignored_kwargs):
    # GPIOZ is one first module to close down: update operational status
    service_is_running_callbacks.run_callbacks(0)

    # Need to close down input and output devices explicitly here
    # Otherwise we run into some trouble with the garbage collector and the automatic GPIOZero shutdown routines
    # I have not understood why yet, but this solves the issue for now
    for n, d in output_devices.items():
        d.close()
    for n, d in input_devices.items():
        d.close()
