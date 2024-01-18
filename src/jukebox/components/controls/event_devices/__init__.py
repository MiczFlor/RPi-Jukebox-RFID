"""
Plugin to register event_devices (ie USB controllers, keyboards etc) in a
    generic manner.

This effectively does:

    * parse the configured event devices from the evdev.yaml
    * setup listen threads

"""
from __future__ import annotations

import logging
from typing import Callable

import jukebox.cfghandler
import jukebox.plugs as plugin
import jukebox.utils
from components.controls.common.evdev_listener import EvDevKeyListener

logger = logging.getLogger("jb.EventDevice")
cfg_main = jukebox.cfghandler.get_handler("jukebox")
cfg_evdev = jukebox.cfghandler.get_handler("eventdevices")

# Keep track of all active key event listener threads
# Removal of dead listener threads is done in lazy fashion:
# only on a new connect are dead threads removed
listener: list[EvDevKeyListener] = []
# Running count of all created listener threads for unique thread naming IDs
listener_cnt = 0

#: Indicates that the module is enabled and loaded w/o errors
IS_ENABLED: bool = False
#: The path of the config file the event device configuration was loaded from
CONFIG_FILE: str

@plugin.register
def activate(
    device_name: str,
    button_callbacks: dict[int, Callable],
    exact: bool = True,
    mandatory_keys: set[int] | None = None,
):
    """Activate an event device listener

    :param device_name: device name
    :type device_name: str
    :param button_callbacks: mapping of event
        code to RPC
    :type button_callbacks: dict[int, Callable]
    :param exact: Should the device_name match exactly
        (default, false) or be a substring of the name?
    :type exact: bool, optional
    :param mandatory_keys: Mandatory event ids the
        device needs to support. Defaults to None
        to require all ids from the button_callbacks
    :type mandatory_keys: set[int] | None, optional
    """
    global listener
    global listener_cnt
    logger.debug("activate event device: %s", device_name)
    # Do a bit of housekeeping: Delete dead threads
    listener = list(filter(lambda x: x.is_alive(), listener))
    # Check that there is no running thread for this device already
    for thread in listener:
        if thread.device_request == device_name and thread.is_alive():
            logger.debug(
                "Event device listener thread already active for '%s'",
                device_name,
            )
            return

    listener_cnt += 1
    new_listener = EvDevKeyListener(
        device_name_request=device_name,
        exact_name=exact,
        thread_name=f"EvDevKeyListener-{listener_cnt}",
    )

    listener.append(new_listener)
    if button_callbacks is not None:
        new_listener.button_callbacks = button_callbacks
    if mandatory_keys is not None:
        new_listener.mandatory_keys = mandatory_keys
    else:
        new_listener.mandatory_keys = set(button_callbacks.keys())
    new_listener.start()


@plugin.initialize
def initialize():
    """Initialize event device button listener from config

    Initializes event buttons from the main configuration file.
    Please see the documentation `builders/event-devices.md` for a specification of the format.
    """
    global IS_ENABLED
    global CONFIG_FILE
    IS_ENABLED = False
    # TODO: chagnge to https://github.com/votti/RPi-Jukebox-RFID/blob/38b4cd4617c5efdabf1ff3e4a513a89e518f8eb2/src/jukebox/components/gpio/gpioz/plugin/__init__.py
    enable = cfg_main.setndefault('evdev', 'enable', value=False)
    CONFIG_FILE = cfg_main.setndefault('evdev', 'config_file', value='../../shared/settings/gpioz.yaml')
    if not enable:
        return
    try:
        jukebox.cfghandler.load_yaml(cfg_evdev, CONFIG_FILE)
    except Exception as e:
        logger.error(f"Disable GPIOZ due to error loading GPIOZ config file. {e.__class__.__name__}: {e}")
        return

    IS_ENABLED = True

    with cfg_evdev:
        for name, config in cfg_evdev.getn(
            "devices",
            default={},
        ).items():
            logger.debug("activate %s", name)
            button_mapping = config.get("mapping", default={})
            button_callbacks: dict[int, Callable] = {}
            for key, action_request in button_mapping.items():
                button_callbacks[key] = jukebox.utils.bind_rpc_command(
                    action_request,
                    dereference=False,
                    logger=logger,
                )
            device_name = config.get("device_name")
            exact = config.get("exact", default=False)
            logger.debug(
                f'Call activate with: "{device_name}" and exact: {exact}',
            )
            activate(
                device_name,
                button_callbacks=button_callbacks,
                exact=exact,
            )


@plugin.atexit
def atexit(**ignored_kwargs):
    global listener
    for ll in listener:
        ll.stop()
    return listener
