Jukebox Apps
===============

The Jukebox's core apps are located in ``src/jukebox``. Run the following command to learn more about each app and its parameters:

.. code-block:: bash

  $ ./run_app_name.py -h

Jukebox Core
*****************

run_jukebox.py
---------------

.. automodule:: run_jukebox

Configuration Tools
********************

Before running the configuration tools, stop the Jukebox Core service.
See :ref:`userguide/configuration:Best practice procedure`.

run_configure_audio.py
-----------------------------

.. automodule:: run_configure_audio

run_register_rfid_reader.py
-----------------------------

.. automodule:: run_register_rfid_reader

Developer Tools
*****************

run_rpc_tool.py
---------------

.. automodule:: run_rpc_tool

run_publicity_sniffer.py
-------------------------

.. automodule:: run_publicity_sniffer

run_sphinx.sh
-------------------------

This command rebuilds the documentation using a Sphinx flow, located in the main directory.

The documentation is built partially from auto-generated RST-files.
Thee files contain the :ref:`userguide/rpc_command_reference:RPC Command Reference`
and :ref:`userguide/rpc_command_alias_reference:RPC Command Alias Reference`.

.. code-block:: bash

    run_jukebox.py -a

The above command regenerate these RST files. This only needs to be done when
the RPC call references need to be updated within the documentation flow.
