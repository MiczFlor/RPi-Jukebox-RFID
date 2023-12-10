# Concepts

The Jukebox is based on three concepts. Don't worry, we won't dive into all the juicy developer details (just yet). But a rough understanding is important as a foundation to understand the configuration files.

## Plugin Interface

The core app is centered around a plugin concept. This serves three purposes:

1. Dynamically load packages with additional functionality based on configuration files.
2. Initialize and close these packages at app start/close. This happens automatically in the background. Failing packages (for any reason) are ignored during start-up. So when some functionality is not available, always check the logs to ensure all packages have loaded successfully! See [Troubleshooting](troubleshooting.md).
3. Register and present functions that can be called via the [Remote Procedure Call Server (RPC)](#remote-procedure-call-server-rpc).

## Remote Procedure Call Server (RPC)

The Remote Procedure Call (RPC) server allows remotely triggering actions (e.g., from the Webapp) within the Jukebox core application. Only Python functions registered by the plugin interface can be called. This simplifies external APIs and lets us focus on the relevant user functions.

Why should you care? Because we use the same protocol when triggering actions from other inputs like a card swipe, a GPIO button press, etc. How that works is described in [RPC Commands](rpc-commands.md).

We also have a [tool to send RPC commands](../developers/coreapps.md#RPC) to the running Jukebox application.

## Publishing Message Queue

The Publishing Message Queue is the complementary part to the RPC where the core application publishes its status and status updates. As a user, you need not worry about it.

If you want to interact with the Jukebox from your own application, this is where you get the current state from. Details about the protocol can be found here (TBD). A [sniffer tool](../developers/coreapps.md#Publicity-Sniffer) exists which listens and prints the incoming status messages.
