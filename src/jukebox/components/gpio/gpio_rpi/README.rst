.. |[X]| unicode:: 0x2611
.. |[ ]| unicode:: 0x2610

----------------------
GPIO RPI
----------------------

The GPIO Module is intended to control Major Jukebox functions such as Start / Stop  Previous/ Next Song via the Raspberry PIs general Purpose I/O Pins

Typical controls like Buttons or Encoders can be attached to theses Pins
These Pins can be assosiated to specifc RPC Commands


GPIO Configuration
---------------------

The GPIO Moule is configured via a yaml file, typically the gpio.yaml

.. code-block:: yaml

    devices:
        PlayPause:
            Type: Button
            Pin: 25
            pull_up_down: pull_up
            edge: falling
            Function: {alias: toggle}


Device Types
-----------------------

Button
^^^^^^^^^^^^^^^^^

|[ ]| Take over Documentation from V2

.. code-block:: yaml

        Button_Name:
            Type: Button
            Pin: 25
            pull_up_down: pull_up
            edge: falling
            Function: {alias: toggle}

RockerButton
^^^^^^^^^^^^^^^^^
    
This is the former Two Button Control
    
|[ ]| Needs implementation

RotaryEncoder
^^^^^^^^^^^^^^^^^
.. code-block:: yaml

  volume:                                               # Name
    Type: RotaryEncoder                                 # Type of this Device
    Pins: [7, 8]                                        # I/O Pins
    FunctionCW: {alias: inc_volume, kwargs: {step: 1}}  # RPC Command called when turning ClockWise
    FunctionCCW:  {alias: dec_volume,kwargs: {step: 1}} # RPC Command called when turning CounterClockWise
    action_after_increments: 1                          # Optional, Resolution, default is 2

PortOut
^^^^^^^^^^^^^^^^^

|[ ]| Needs implementation (in Progress)

API:

* SetPortState(self, name, state)

.. code-block:: yaml

  My_first_GPIO:                                        # Name
    Type: PortOut                                       # Type of this Device
    Pins: [25]                                          # Pins for this Output
    States: {On: [1], Off: [0]}                         # States definition


Th GPIO Module support to set more pins in parallel per state.
E.g. dual- or multicolor LEDs could be supported in that way.

.. code-block:: yaml

  DUAL_COLOR_LED:                                       # Name
    Type: PortOut                                       # Type of this Device
    Pins: [22,21]                                       # Pins for this Output
    States: {RED: [1, 0], GREEN: [0, 1], OFF: [0, 0]}   # States definition

The Order in the List of the State is following the order of the pins before.
So in the above case "RED: [1, 0]"" means Pin 22 = 1, Pin 21 = 0


Squences
~~~~~~~~~~~~~~~~~~~~~~

API:

* StartPortSequence(PortName, Sequence)
* StopPortSequence(PortName)


.. code-block:: yaml   
   
   seq:  [{state:  On, delay: 200},     # state to be set, deley in ms
          {state: Off, delay: 200},
          {state:  On, delay: 200},
          {state: Off, delay: 200}]


to support blinking the sequenzer understands the keyword repeat, which will start the squenze from beginning

.. code-block:: yaml

    seq:  [{state: Off, delay: 200},   # state to be set, deley in ms
           {state:  On, repeat: 200}]  # state to be set, deley in ms before the sequence is repeated


