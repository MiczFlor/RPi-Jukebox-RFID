-Controls based on EvDev input devices
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^


Common
*************************

This contains generic modules to interact with Event Devices (USB, bluetooth and other peripherals listed under /dev/input).

.. automodule:: components.controls.common.evdev_listener
    :members:
    :private-members: _filter_by_device_name, _filter_by_mandatory_keys

Bluetooth audio buttons
*************************

See also the corresponding user guide :ref:`userguide/bluetooth_audio_buttons:Bluetooth audio buttons`

.. automodule:: components.controls.bluetooth_audio_buttons
    :members:

Event Devices
*************

See also the corresponding user guide :ref:`userguide/event_devices:Event Devices`

.. automodule:: components.controls.event_devices
    :members: