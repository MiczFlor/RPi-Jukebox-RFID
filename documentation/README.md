# Welcome to RPi Jukebox RFID’s documentation!

The exciting, new Version 3 of the RPi Jukebox RFID. A complete rewrite of the Jukebox code base.

> [!NOTE]
> This documentation applies to the Version 3 which is developed in the branches `future3/main` and `future3/develop`. Currently the default Version is 2.x

To find out more about the RPi Jukebox RFID
project check out the [documentation of Version 2](https://github.com/MiczFlor/RPi-Jukebox-RFID) or [www.phoniebox.de](https://www.phoniebox.de/).

## Quickstart

* For Builders: Building a Phoniebox
  * [Installing Phoniebox future3](./content/userguide/installation.md)
  * [User Guide](./content/userguide/README.md)
  * [Update](./content/userguide/update.md)
* For Developers: Add features or fix bugs
  * [Developer Reference](./content/developers/README.md)
  * [Feature Status](./content/developers/status.md)
  * [Known Issues](./content/developers/known-issues.md)

## future3

### Why?

* Better extensibility, clear architecture allowing for easier integration of new features
* Higher performance especially on lower end hardware (it's a stretch at the moment)
* Better maintainability
* Better observability for debugging

### How?

* Jukebox core is a holistic Python3-only application
* Avoid shell script invocation during runtime wherever possible
* Establish a socket based API (using ZeroMQ) toward the WebUI or other clients
* Implemented a Remote-Procedure-Call (RPC) server through which all user function calls pass
* Implemented a plugin concept to dynamically load Python modules configurable through the configuration file
* In conjunction with the RPC, this is a neat way of allowing additional features without having to touch the core all the time

### Where are we? Help wanted!

The initial proof-of-concept phase has been left behind and there is quite some functionality available already.
This is still an ongoing process but the WebUI and RFID-triggered playback of local files work.

Features/files from version 2.X will only be copied/merged once they can be integrated and tested.
If you don't find your v2.X contributions, it doesn't mean they are obsolete. Things will be integrated step by step.
And, of course, you are welcome to adapt your previous contributions to this new exiting structure.
