.. |[X]| unicode:: 0x2611
.. |[ ]| unicode:: 0x2610

----------------------
GPIO RPI
----------------------

The GPIO module is intended to control major Jukebox functions such as Start/Stop or Previous Song/Next Song via the Raspberry Pi's general purpose I/O pins.

Typical controls like buttons or encoders can be attached to these pins, assosiated to specifc RPC commands.


GPIO Configuration
---------------------

The GPIO moule is configured via a yaml file, typically ``gpio.yaml``.

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

|[ ]| Take over documentation from V2

.. code-block:: yaml

        Button_Name:
            Type: Button
            Pin: 25
            pull_up_down: pull_up
            edge: falling
            Function: {alias: toggle}

RockerButton
^^^^^^^^^^^^^^^^^
    
This is the former 2-Button control
    
|[ ]| Needs implementation

RotaryEncoder
^^^^^^^^^^^^^^^^^
.. code-block:: yaml

  volume:                                               # Name
    Type: RotaryEncoder                                 # Device type
    Pins: [7, 8]                                        # I/O pins
    FunctionCW: {alias: inc_volume, kwargs: {step: 1}}  # RPC command called when turning [c]lock[w]ise
    FunctionCCW:  {alias: dec_volume,kwargs: {step: 1}} # RPC command called when turning [c]ounter[c]lock[w]ise
    action_after_increments: 1                          # [Optional] Resolution, default is 2

PortOut
^^^^^^^^^^^^^^^^^

|[ ]| Needs implementation (in progress)

API:

* SetPortState(self, name, state)

.. code-block:: yaml

  My_first_GPIO:                                        # Name
    Type: PortOut                                       # Device type
    Pins: [25]                                          # Pins for this output
    States: {On: [1], Off: [0]}                         # States definition


The GPIO module supports mulitple pins simultaneously per state.
This way, dual- or multicolor LEDs are supported.

.. code-block:: yaml

  DUAL_COLOR_LED:                                       # Name
    Type: PortOut                                       # Device type
    Pins: [22, 21]                                      # Pins for this output
    States: {RED: [1, 0], GREEN: [0, 1], OFF: [0, 0]}   # States definition

The order states is following the order of the pins before.
So in the above case ``RED: [1, 0]`` means pin ``22 = 1``, pin ``21 = 0``.


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


To support blinking, the sequencer understands the keyword ``repeat`` which will start the sequence from the beginning.

.. code-block:: yaml

    seq:  [{state: Off, delay: 200},   # state to be set, deley in ms
           {state:  On, repeat: 200}]  # state to be set, deley in ms before the sequence is repeated


