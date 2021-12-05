Generic USB Reader
-------------------------

**place-capable**: typically no

This module covers all types of USB-based RFID input readers. If you plan to connect multiple USB-based
RFID readers to the Jukebox, make sure to connect all of them before running
the registration tool :ref:`developer/coreapps:run_register_rfid_reader.py`.

.. note:: The user needs to be part of the group 'input' for evdev to work.
    This should usually be the case. However, a user can be added with:

    .. code-block:: bash

        sudo usermod -a -G input USER

