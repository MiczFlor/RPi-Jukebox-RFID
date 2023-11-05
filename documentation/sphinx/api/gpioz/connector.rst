.. RPI Jukebox RFID Version 3
.. Copyright (c) See file LICENSE in project root folder

-------------------------------
GPIOZ Connector Functions
-------------------------------

.. automodule:: components.gpio.gpioz.plugin.connectivity

.. currentmodule:: components.gpio.gpioz.plugin.connectivity

Common
^^^^^^^^

.. autoattribute:: components.gpio.gpioz.plugin.connectivity.BUZZ_TONE

RFID
^^^^^

.. autofunction:: register_rfid_callback


Volume
^^^^^^^^

.. autofunction:: register_volume_led_callback

.. autofunction:: register_volume_rgbled_callback

.. autofunction:: register_volume_buzzer_callback

Audio output sink
^^^^^^^^^^^^^^^^^^

.. autofunction:: register_audio_sink_change_callback

Status
^^^^^^^^
.. autofunction:: register_status_led_callback

.. autofunction:: register_status_buzzer_callback

.. autofunction:: register_status_tonalbuzzer_callback


