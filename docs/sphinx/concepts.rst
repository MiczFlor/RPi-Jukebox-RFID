Concepts
================================================

The Jukebox is based on three concepts. Don't worry we won't delve into all the juicy developer details.
But a rough understanding is important as this foundation reverberates into the configuration files.

Plugin Interface
----------------

The core app is centered around a plugin concept. This serves three purposes:

    #. Dynamically load packages with additional functionality based the configuration file.
    #. Initialize and close these packages at app start / close. This happens in the background. Failing
       packages (for any reason) are ignored during start-up. So when some functionality is not available, always
       check the logs to ensure all packages have loaded successfully! See :ref:`coreapps:Troubleshooting`.
    #. Register and present functions which can be called via the :ref:`concepts:Remote Procedure Call Server (RPC)`

That's about what you need to know for the plugin concept. Developer detail information
can be found here (TBD).

Remote Procedure Call Server (RPC)
--------------------------------------

The Remote Procedure Call (RPC) Server allows to remotely trigger actions (e.g. from the WebUI) in the Jukebox Core App.
Not all Python functions of the core app are callable, but only those registered with the plugin interface. This
is to simplify the external API and focus on the relevant user functions.

Why should you care? Because we use the same protocol when triggering actions from other inputs, say, a card swipe, a
GPIO button press, etc. So, here is the essence of what you need to know:

An RPC call consists of up to three parts

    #. the function to execute (e.g. play_folder, incr_volume)
    #. the positional arguments (optional)
    #. the keyword arguments (optional)

The function specification consists of two e.g. ``host.shutdown`` or three parts ``volume.ctrl.incr_volume``. In
configuration files, this will look like this:

.. code-block:: yaml

        package: host
        plugin: shutdown

Or like this for a three part function with the argument set to ``5``:

.. code-block:: yaml

        package: volume
        plugin: ctrl
        method: incr_volume
        args: [5]

You will find a full list of RPC callable functions in :ref:`rpc_command_reference:RPC Command Reference` and in
``shared/settings/plugin_reference``. Examples are given in the configuration of the :ref:`carddatabase:Card Database`

For developers the details can be found here (TBD). We also have tool to send RPC commands to the running Jukebox App:
:ref:`coreapps:run_rpc_tool.py`

Publishing Message Queue
--------------------------

The complimentary part to the RPC, where the core app publishes is status and status changes. As a user, you need not
worry about it.

If you want to interface with the Jukebox for your own application, this is where you get the current
state from. Details about the protocol here (TBD). And there is a sniffer tool which listens and prints the incoming
status messages: :ref:`coreapps:run_publicity_sniffer.py`.

