.. RPI Jukebox RFID Version 3
.. Copyright (c) See file LICENSE in project root folder

-------------------------------
GPIOZ Output Devices
-------------------------------

.. automodule:: components.gpio.gpioz.core.output_devices

.. py:currentmodule:: components.gpio.gpioz.core.output_devices


LED
^^^

.. autoclass:: LED(pin, *, active_high=True, initial_value=False, pin_factory=None, name=None)
    :members: flash, on, off, toggle, blink, pin, is_lit, value

PWMLED
^^^^^^^

.. autoclass:: PWMLED(pin, *, active_high=True, initial_value=0, frequency=100, pin_factory=None, name=None)
    :members: flash, on, off, toggle, blink, pulse, pin, is_lit, value


RGBLED
^^^^^^^

.. autoclass:: RGBLED(red, green, blue, *, active_high=True, initial_value=(0, 0, 0), pwm=True, pin_factory=None, name=None)
    :members: flash, on, off, toggle, blink, pulse, red, green, blue, is_lit, color, value


Buzzer
^^^^^^^

.. autoclass:: Buzzer(pin, *, active_high=True, initial_value=False, pin_factory=None, name=None)
    :members: flash, on, off, toggle, beep, pin, is_active, value


TonalBuzzer
^^^^^^^^^^^^^^

.. autoclass:: TonalBuzzer(pin, *, initial_value=None, mid_tone=Tone('A5'), octaves=2, pin_factory=None, name=None)
    :members: melody, flash, play, stop, octaves, min_tone, mid_tone, max_tone, tone, is_active, value
