.. |[X]| unicode:: 0x2611
.. |[ ]| unicode:: 0x2610

----------------------
GPIO RPI
----------------------

The GPIO module is intended to control major Jukebox functions such as Start/Stop or Previous Song/Next Song via the Raspberry Pi's general purpose I/O pins.

Typical controls like buttons or encoders can be attached to these pins, assosiated to specifc RPC commands.


GPIO Configuration
---------------------

The GPIO moule is configured via a yaml file, typically ``gpio.yaml``. Just create it as shared/settings/gpio.yaml

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

  volume:                                                     # Name
    Type: RotaryEncoder                                       # Device type
    Pins: [7, 8]                                              # I/O pins
    FunctionCW: {alias: change_volume, kwargs: {step: 5}}     # RPC command called when turning [c]lock[w]ise
    FunctionCCW: {alias: change_volume, kwargs: {step: -5}}   # RPC command called when turning [c]ounter[c]lock[w]ise
    action_after_increments: 2                                # [Optional] Resolution, default is 2

PortOut
^^^^^^^^^^^^^^^^^

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


Sequences
~~~~~~~~~~~~~~~~~~~~~~

API:

* StartPortSequence(Sequence)
* StopPortSequence(PortName)

Sequences are controlled via a dictionary containing the fields ``name``, ``mode`` and ``seq``

- `name` is the name of a the PortOut which is to be actuated
- `mode` can have the values ``single`` and ``cont``. 
  If ``single`` is set, the Sequence will be run once, otherwise it will be repeated endlessly
- `seq` is a list of lists containing the State to be set followed by the time in ms:
  
  [ [``State``, ``Time in ms``] , [``State``, ``Time in ms``] ]

  The State must be one of the States defined in the gpio.ymal for the coresponding PortOut

.. code-block:: yaml

    {'name': 'BLUE_LED',
     'mode': 'single',
     'seq': [['On',100],['Off',100],['On',100],['Off',0]]}

.. code-block:: yaml

    {'name': 'RED_LED',
     'mode': 'cont',
     'seq': [['On',100],['Off',100],['On',100],['Off',100]]}


