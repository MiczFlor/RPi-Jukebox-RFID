"""
When a bluetooth sound device (headphone, speakers) connects
attempt to automatically listen to it's buttons (play, next, ...)

The bluetooth input device name is matched automatically from the
bluetooth sound card device name. During boot up, it is uncertain if the bluetooth device connects first,
or the Jukebox service is ready first. Therefore,
after service initialization, already connected bluetooth sound devices are scanned and an attempt is made
to find their input buttons.

.. note:: If the automatic matching fails, there currently is no
    manual configuration option

Button key codes are standardized and by default the buttons
play, pause, next song, previous song are recognized. Volume up/down is handled independently
from this module by PulseAudio and the bluetooth audio transmission protocol.

The module needs to be enabled in the main configuration file with:

.. code-block:: yaml

    bluetooth_audio_buttons:
      enable: true


Custom key bindings
---------------------

You may change or extend the actions assigned to a button in the configuration. If the configuration contains
a block 'mapping', the default button-action mapping is *completely* replaced with the new mapping. The definitions for
each key looks like ``key-code: {rpc_command_definition}``.
The RPC command follows the regular RPC command rules as defined in :ref:`userguide/rpc_commands:RPC Commands`.

.. code-block:: yaml

    bluetooth_audio_buttons:
      enable: true
      mapping:
        # Play & pause both map to toggle which is also the usual behaviour of headsets
        200:
          alias: toggle
        201:
          alias: toggle
        # Re-map next song button, to set defined output volume (for some fun)
        163:
          package: volume
          plugin: ctrl
          method: set_volume
          args: [18]
        # Re-map prev song button to shutdown
        165:
          alias: shutdown


Key codes can be found in the log files. Press the various buttons on your headset, while watching the
logs with e.g. ``tail -f shared/logs/app.log``.  Look for entries like ``No callback registered for button ...``.
"""
import logging
import jukebox.plugs as plugin

from typing import (List, Callable, Dict)
from components.controls.evdev_listener import EvDevKeyListener

import jukebox.cfghandler
import jukebox.utils
import components.volume

logger = logging.getLogger('jb.BtButtons')
cfg = jukebox.cfghandler.get_handler('jukebox')

# Keep track of all active key event listener threads
# Removal of dead listener threads is done in lazy fashion: only on a new connect are dead threads removed
listener: List[EvDevKeyListener] = []
# Running count of all created listener threads for unique thread naming IDs
listener_cnt = 0

# During initialization, the callback mapping is built once
# and re-used for all connecting bluetooth devices
button_callbacks: Dict[int, Callable] = {}

# Standardized button key codes
bt_keycode_play = 200
bt_keycode_pause = 201
bt_keycode_next = 163
bt_keycode_prev = 165

# When opening a device as input device, expect at least a play button
mandatory_keys = {bt_keycode_play}


@plugin.register
def activate(device_name: str, exact: bool = True, open_initial_delay: float = 0.25):
    global listener
    global listener_cnt
    # Do a bit of housekeeping: Delete dead threads
    listener = list(filter(lambda x: x.is_alive(), listener))
    # Check that there is no running thread for this device already
    for ll in listener:
        if ll.device_request == device_name and ll.is_alive():
            logger.debug(f"Button listener thread already active for '{device_name}'")
            return

    listener_cnt += 1
    new_listener = EvDevKeyListener(device_name_request=device_name, exact_name=exact,
                                    thread_name=f'BtKeyListener-{listener_cnt}')

    listener.append(new_listener)
    new_listener.button_callbacks = button_callbacks
    new_listener.mandatory_keys = mandatory_keys
    # When coming from volume.py on new card callback, we need to wait wee while here before input device is available
    # This delay is applied in listener thread!
    new_listener.open_initial_delay = open_initial_delay
    new_listener.start()


def activate_from_pulse(card_driver: str, device_name: str):
    if card_driver == 'module-bluez5-device.c':
        activate(device_name, exact=False)
    else:
        logger.info(f"Ignoring activation request from non-bluetooth module '{card_driver}'")


@plugin.initialize
def initialize():
    if cfg.setndefault('bluetooth_audio_buttons', 'enable', value=True):
        components.volume.add_on_connect_callback(activate_from_pulse)
        button_mapping = cfg.getn('bluetooth_audio_buttons', 'mapping', default=None)
        if button_mapping:
            for key, action_request in button_mapping.items():
                button_callbacks[key] = jukebox.utils.bind_rpc_command(action_request, logger)
        else:
            # Create default mapping
            button_callbacks[bt_keycode_play] = jukebox.utils.bind_rpc_command({'alias': 'toggle'}, logger)
            button_callbacks[bt_keycode_pause] = jukebox.utils.bind_rpc_command({'alias': 'toggle'}, logger)
            button_callbacks[bt_keycode_next] = jukebox.utils.bind_rpc_command({'alias': 'next_song'}, logger)
            button_callbacks[bt_keycode_prev] = jukebox.utils.bind_rpc_command({'alias': 'prev_song'}, logger)

        # The is a potential start-up race condition:
        # The activation callback from the PulseAudio plugin only gets executed when a new sound card connects
        # If a bluetooth device connects faster than this service boots, we might never see the
        # callback. So, at this point, we simply try to connect to all connected sound card bluetooth devices
        # It is no issue, if they have been connected by callback in between either: we only get an additional debug log entry
        sound_cards = components.volume.pulse_control.card_list()
        for s in sound_cards:
            if s.driver == 'module-bluez5-device.c':
                device_name = s.proplist.get('device.description', None)
                if device_name:
                    logger.debug(f"Speculative start-up activation of buttons on bluetooth sound device '{device_name}'")
                    activate(device_name, exact=False, open_initial_delay=0.1)


@plugin.atexit
def atexit(**ignored_kwargs):
    global listener
    for ll in listener:
        ll.stop()
    return listener
