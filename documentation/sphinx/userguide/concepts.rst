Concepts
================================================

The Jukebox is based on three concepts. Don't worry we won't dive into all the juicy developer details (just yet).
But a rough understanding is important as an foundation to understand the configuration files.

Plugin Interface
----------------

The core app is centered around a plugin concept. This serves three purposes:

    #. Dynamically load packages with additional functionality based on configuration files.
    #. Initialize and close these packages at app start / close. This happens automatically in the background. Failing
       packages (for any reason) are ignored during start-up. So when some functionality is not available, always
       check the logs to ensure all packages have loaded successfully! See :ref:`userguide/troubleshooting:Troubleshooting`.
    #. Register and present functions which can be called via the :ref:`userguide/concepts:Remote Procedure Call Server (RPC)`

That's about what you need to know for the plugin concept. Developer detailed information
can be found here (TBD).

Remote Procedure Call Server (RPC)
--------------------------------------

The Remote Procedure Call (RPC) server allows to remotely trigger actions (e.g., from the Webapp) within the Jukebox core application.
Only Python functions registered by the plugin interface can be called. This
simplifies external APIs and let's us focus on the relevant user functions.

Why should you care? Because we use the same protocol when triggering actions from other inputs like a card swipe, a
GPIO button press, etc. How that works is described in :ref:`userguide/rpc_commands:RPC Commands`.

You will find a full list of RPC callable functions in :ref:`userguide/rpc_command_reference:RPC Command Reference`
and aliases for convinience in :ref:`userguide/rpc_command_alias_reference:RPC Command Alias Reference`

For developers the details can be found here (TBD). We also have a tool to send RPC commands to the running Jukebox application:
:ref:`developer/coreapps:run_rpc_tool.py`

Publishing Message Queue
--------------------------

The Publishing Message Queue is the complimentary part to the RPC where the core application publishes its status and status updates.
As a user, you need not worry about it.

If you want to interact with the Jukebox from your own application, this is where you get the current
state from. Details about the protocol can be found here (TBD). A sniffer tool exists which listens and prints the incoming
status messages: :ref:`developer/coreapps:run_publicity_sniffer.py`.

