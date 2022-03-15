.. RPI Jukebox RFID
.. Copyright (c) 2021 Chris Banz
..
.. SPDX-License-Identifier: MIT License

-------------------------------
GPIOZ Input Devices
-------------------------------

.. automodule:: components.gpio.gpioz.core.input_devices

.. currentmodule:: components.gpio.gpioz.core.input_devices

Button
^^^^^^^^

.. autoclass:: Button
    :members: on_press, set_rpc_actions, close, value, pull_up, pin, hold_time, hold_repeat

Long press Button
^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. autoclass:: LongPressButton
    :members: on_press, set_rpc_actions, close, value, pull_up, pin, hold_time, hold_repeat

Short + Long press Button
^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. autoclass:: ShortLongPressButton
    :members: on_short_press, on_long_press, set_rpc_actions, close, value, pull_up, pin, hold_time, hold_repeat

Twin Button
^^^^^^^^^^^^^^^^^^^

.. autoclass:: TwinButton
    :members:  on_short_press_a, on_short_press_b, on_short_press_ab, on_long_press_a, on_long_press_b, on_long_press_ab, value, is_active, hold_repeat, hold_time, close

Rotary Encoder
^^^^^^^^^^^^^^^^^^

.. autoclass:: RotaryEncoder
    :members: on_rotate_clockwise, on_rotate_counter_clockwise, set_rpc_actions, close, pin_a, pin_b


