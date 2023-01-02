Event devices are generic input devices that are exposed in  /dev/input.
This includes USB peripherals (Keyboards, Controllers, Joysticks or Mouse) as well as potentially bluetooth devices.

The devices and their button mappins need to be mapped in the configuration file.

Configuration
---------------------

To configure event devices, first add the plugin as the last entry to the module list:

.. code-block:: yaml

  modules:
    named:
      event_devices: controls.event_devices # Add as last entry

Then add the following section to the configuration:

.. code-block:: yaml

  event_devices:
    devices: # list of devices to listen for
      {device nickname}: # config for a specific device
        device_name: {device_name} # name of the evdev
        exact: False/True # optional to require exact match
        mapping:
          {key-code}: # evdev event id
              {rpc_command_definition} # eg `alias: toggle` 

The ``{device nickname}`` is only for your own orientation and can be choosen freely.
For each device you need to figure out the ``{device_name}`` and the ``{event_id}`` corresponding to button presses.

``{device_name}``
==================

The ``{device_name}`` can be identified using the following Python snippet:

.. code-block:: Python

  import evdev
  devices = [evdev.InputDevice(path) for path in evdev.list_devices()]
  for device in devices:
      print(device.path, device.name, device.phys)

The output could be in the style of: ::

  /dev/input/event1    Dell Dell USB Keyboard   usb-0000:00:12.1-2/input0
  /dev/input/event0    Dell USB Optical Mouse   usb-0000:00:12.0-2/input0

In this example, the ```{device_name}``` could be ``DELL USB Optical Mouse``.
Note that if you use the option ``exact: False``, it would be sufficient to add a substring such as ``USB Keyboard``.

``{key-code}``
================

The key code for a button press can be determined using the following code snippet:

.. code-block:: Python

  import evdev
  device = evdev.InputDevice('/dev/input/event0')
  device.capabilities(verbose=True)[('EV_KEY', evdev.ecodes.EV_KEY)]

with the InputDevice corresponding to the path from the output of the section ```{device_name}``` (eg. in the example ``/dev/input/event0``
would correspond to the ``Dell Dell USB Keyboard``).

If the naming is not clear, it is also possible to empirically check for the button code by listening for events:

.. code-block:: Python

  from evdev import InputDevice, categorize, ecodes
  dev = InputDevice('/dev/input/event1')
  print(dev)
  for event in dev.read_loop():
    if event.type == ecodes.EV_KEY:
      print(categorize(event))

The output could be of the form::
  device /dev/input/event1, name "DragonRise Inc.   Generic   USB  Joystick  ", phys "usb-3f980000.usb-1.2/input0"
  key event at 1672569673.124168, 297 (BTN_BASE4), down
  key event at 1672569673.385170, 297 (BTN_BASE4), up

In this example output, the ``{key-code}`` would be ``297``

Alternatively, the device could also be setup without mapping.
Afterwards, when pressing keys, the Key codes can be found in the log files. Press the various buttons on your device,
while watching the logs with e.g. ``tail -f shared/logs/app.log``.
Look for entries like ``No callback registered for button ...``.

``{rpc_command_defintion}``
==============================
Each key looks like ``{key-code}: {rpc_command_definition}``.
The RPC command follows the regular RPC command rules as defined in :ref:`userguide/rpc_commands:RPC Commands`.


Full example config
=====================

Here is a complete example configuration for a USB Joystick controller:

.. code-block:: yaml
  
  event_devices:
    devices:
      joystick:
        device_name: DragonRise Inc.   Generic   USB
        exact: false
        mapping:
          299:
            alias: toggle
          298:
            alias: next_song
          297:
            alias: prev_song
          296:
            alias: change_volume
            args: 5
          295:
            alias: change_volume
            args: -5
          # Button to set defined output volume
          291:
            package: volume
            plugin: ctrl
            method: set_volume
            args: [18]
          # Button to shutdown
          292:
            alias: shutdown


Key codes can be found in the log files. Press the various buttons on your headset, while watching the
logs with e.g. ``tail -f shared/logs/app.log``.  Look for entries like ``No callback registered for button ...``.