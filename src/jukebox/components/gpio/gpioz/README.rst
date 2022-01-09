GPIO Recipes
**************

Enabling GPIO
----------------

The GPIO module needs to be enabled in your main configuration file ``shared/settings/jukebox.yaml``. Look for the
this entry and modify it accordingly:

.. code-block:: yaml

        gpioz:
          enable: true
          config_file: ../../shared/settings/gpioz.yaml

The GPIO configuration itself is stored in a separate file, in this case ``../../shared/settings/gpioz.yaml``.
I am sure you see the connection.

The GPIO module uses `GPIOZero <https://gpiozero.readthedocs.io/>`_ as a backend to the the RPis GPIO Pins. It is
only relatively thinly wrapped to integrate it into the Jukebox's API, provide YAML based configuration, and provide
helpful error messages on misconfiguration.

The pin numbering is the BCM pin numbering, as is the
`default in GPIOZero <https://gpiozero.readthedocs.io/en/stable/recipes.html#pin-numbering>`_.

The GPIOZ configuration file has the following structure:

.. code-block:: yaml

    pin_factory:
      type: rpigpio.RPiGPIOFactory
    output_devices:
      ...
    input_devices:
      ...

The is no need to touch the header - there are only `Developer options`_ here.

A sample file is provided in ``resources/default-settings/gpioz.yaml``. Below you will find easy to adapt recipes for
various configuration snippets.


Input devices
---------------

Configuring input devices consists of two aspects:

    #. Define an input device and configure it's parameters
    #. Assign an action to execute on input state change.
       Actions are defined as :ref:`userguide/rpc_commands:RPC Commands`
       just the same as for assigning card actions.


Button: Toggle Playback
^^^^^^^^^^^^^^^^^^^^^^^^

A button to toggle music playback on single press:

.. code-block:: yaml

    input_devices:
      TogglePlayback:
        type: Button
        kwargs:
          pin: 13
        actions:
          on_press:
            alias: toggle

The ``type`` is an input device from the Python module TBD. With ``kwargs`` you can set all the class initialization
parameters. Usually, only the pin(s) are mandatory parameters. In the section ``actions``, the RPC commands are linked,
either as alias (i.e. shortcut) or full RPC command specification.

Each device instantiation must be uniquely named, here  ``TogglePlayback``. The name can be freely chosen, as
long as it is unique.

The default configuration of the Button uses the internal pull-up resistor. So, the physical connection to
the RPi looks like this

.. code-block:: text

 ----+
     |      1 kOhm   Button
   13| -----======------/ ----+
     |                        |
 ----+                        - GND

Button: Increase volume
^^^^^^^^^^^^^^^^^^^^^^^^

A button to increase the volume by 5 steps every 0.75 second as long as it is held:

.. code-block:: yaml

    input_devices:
      IncreaseVolume:
        type: Button
        kwargs:
          pin: 13
          hold_time: 0.75
          hold_repeat: True
        actions:
          on_press:
            alias: change_volume
            args: +5

Button: Shutdown
^^^^^^^^^^^^^^^^^^^^^^^^

A button to shutdown the Jukebox if it is held for more than 3 seconds. Note the different ``type`` here!

.. code-block:: yaml

    input_devices:
      IncreaseVolume:
        type: LongPressButton
        kwargs:
          pin: 13
          hold_time: 3
        actions:
          on_press:
            alias: change_volume
            args: +5

Button: Dual Action
^^^^^^^^^^^^^^^^^^^^^^^^

A button to act differently on short and long press. Go to previous song on single short press, start playlist from
the beginning on press longer than 1 second. Note: the short press action is executed on button release since we
don't not know how much longer somebody is going to press the button. The long press action is executed as soon
as the hold time has been reached.

.. code-block:: yaml

    input_devices:
      PreviousSong:
        type: ShortLongPressButton
        kwargs:
          pin: 13
          hold_time: 1
        actions:
          on_short_press:
            alias: prev_song
          on_long_press:
            alias: replay


Rotary Encoder: Volume Control
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

A rotary encoder to change the volume. A common module is the KY-040, which can be picked up from numerous shops.
It has four pins, typically labelled DT, CLK, SW, GND. Connect GND to ground. Connect DT and CLK to the
RPi with a 1 kOhm resistor each - these are pins ``a`` in ``b`` in the configuration. If later the rotation
direction does not match, simply swap the pins in the configuration file. The pin SW (for switch) is not always
present. It is a button when the rotary encoder is pressed from the top. Configure a
`regular button entry <Button: Toggle Playback>`_ separately for this button.

.. code-block:: yaml

    input_devices:
      VolumeRotator:
        type: RotaryEncoder
        kwargs:
          a: 5
          b: 6
        actions:
          on_rotate_clockwise:
            alias: change_volume
            args: 5
          on_rotate_counter_clockwise:
            alias: change_volume
            args: -5

Rotary Encoder: Previous/Next Song
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

From the previous recipe, simply replace the actions to have a rotary encoder to step through the playlist:

.. code-block:: yaml

        ...
        actions:
          on_rotate_clockwise:
            alias: next_song
          on_rotate_counter_clockwise:
            alias: prev_song


Output devices
--------------

Configuring output devices contains two aspects:

    #. Define the the output device
    #. Connect the device to some Jukebox function which then
       activates the device on e.g. RFID card read. There are many predefined connections
       available. New connections can also be coded in the Python. More information here (TBD).

As output devices, all output devices of GPIOZero can be used. The intelligence in using the output
lies in the connectivity function. The predefined functions can be found here - not every function
can support every output device.

Status LED
^^^^^^^^^^^^^^

An LED that lights up, when the Jukebox service is operational.

As with the input devices, every output device requires a unique, but freely chosen name - here ``StatusLED``.
The parameter ``type`` directly matches the `GPIOZero output devices
<https://gpiozero.readthedocs.io/en/stable/api_output.html#regular-classes>`_.
The parameters in ``kwargs`` relate to the class initialization parameters.

The ``connect`` option is a list of functions to call to connect this device with a function inside
the Jukebox. An output device can be used by multiple functions.

.. code-block:: yaml

    output_devices:
      StatusLED:
        type: LED
        connect:
          - gpio.gpioz.plugin.connectivity.register_status_led_callback
        kwargs:
          pin: 17

Card Read Buzzer
^^^^^^^^^^^^^^^^^^

Sound a Piezzo Buzzer once when a card swipe has been detected. For unknown cards, sound it three times.

.. code-block:: yaml

    output_devices:
      RfidBuzzer:
        type: Buzzer
        connect:
          - gpio.gpioz.plugin.connectivity.register_rfid_callback
        kwargs:
          pin: 12

Card Read + Status Buzzer
^^^^^^^^^^^^^^^^^^^^^^^^^

Extend the card read buzzer to also sound one long beed after completed boot up and two beeps on shutdown.
The only difference is the second connection function.

.. code-block:: yaml

    output_devices:
      RfidBuzzer:
        type: Buzzer
        connect:
          - gpio.gpioz.plugin.connectivity.register_rfid_callback
          - gpio.gpioz.plugin.connectivity.register_status_buzzer_callback
        kwargs:
          pin: 12

Card Read LED
^^^^^^^^^^^^^^^^^^

Just like `Card Read Buzzer`_, but blink an LED instead of a buzzer. The only difference is the output device type.

.. code-block:: yaml

    output_devices:
      RfidLED:
        type: LED
        connect:
          - gpio.gpioz.plugin.connectivity.register_rfid_callback
        kwargs:
          pin: 12

Volume LED
^^^^^^^^^^^^

Have an LED change it's brightness to reflect the current volume level.

.. code-block:: yaml

    output_devices:
      VolumeLED:
        type: PWMLED
        connect: gpio.gpioz.plugin.connectivity.register_volume_led_callback
        kwargs:
          pin: 18

Bluetooth audio output LED
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Indicates the current audio output sink. LED is off when audio sink is primary sink, and
on when audio sink is secondary sink (e.g. a bluetooth headset). When sink toggle fails, LED blinks
thrice.

.. code-block:: yaml

    output_devices:
      HeadsetConnected:
        type: LED
        connect:
          - gpio.gpioz.plugin.connectivity.register_audio_sink_change_callback
        kwargs:
          pin: 27


Developer options
---------------------

For developers there are two options. Both replace the pin factory used by GPIOZero.

Use Mock Pins
^^^^^^^^^^^^^^^

Using GPIOZero `Mock pins <https://gpiozero.readthedocs.io/en/stable/api_pins.html#mock-pins>`_
, allows to do function development on an arbitrary machine. If you have
configured the :ref:`Mock RFID Reader <rfid/mock_reader:Mock Reader>`,
the GPIO input and output devices are added to the GUI. Simply change the header in the configuration file to:

.. code-block:: yaml

    pin_factory:
      type: mock.MockFactory

.. image:: mock_gpio.png
    :width: 80 %
    :align: center

Use Remote Pins
^^^^^^^^^^^^^^^^^^

Using `GPIOZero's remote pins <https://gpiozero.readthedocs.io/en/stable/remote_gpio.html>`_,
allows to run the Jukebox code on one machine, and have the GPIO
happen on an RPi Board. See the GPIOZero Documentation how to set it up on the machines.
Simply change the header in the configuration file to enable it. Host is the IP address of your RPi Board.

.. code-block:: yaml

    pin_factory:
      type: pigpio.PiGPIOFactory
      pigpio.PiGPIOFactory:
        kwargs:
          host: 192.168.178.32


