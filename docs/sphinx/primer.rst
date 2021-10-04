What is this?
================================================

The exiting, new **Version 3** of the RPi Jukebox RFID. A complete re-write of the Jukebox.

.. important:: This documentation applies to the Version 3 which is developed in the branch *future3/develop*.
    Currently the default Version is 2.X

To find out more about the RPi Jukebox RFID
project check out the `documentation of Version 2 <https://github.com/MiczFlor/RPi-Jukebox-RFID>`_.

Why?
-----

* better maintainability
* better observability for debugging
* clear architecture allowing easier integration of new feature
* higher performance especially on lower end hardware

How?
------

* Jukebox core is a holistic Python3-only application
* Avoid shell script invocation during runtime wherever possible
* Establish a socket based API (using ZeroMQ) toward the WebUI
* Implement a Remote-Procedure-Call (RPC) Server through which all user function call pass
* Implement a plugin-concept to dynamically load additional Python Module for easy extendability
* In conjunction with the RPC this is a neat way of allowing additional feature without having to touch the core all the time

Where are we?
--------------

The initial proof-of-concept phase has been left behind and there already is quite some functionality available.
This is still heavily in progress, but the WebUI and RFID-triggered playback of local files works.

Features/Files form the Version 2.X branch will only be copied/merged when they can be integrated and tested.
If you don't find your v2.X contributions, it doesn't mean they are obsolete. Things will be integrated step by step.
And, of course, you are welcome to adapt your previous contributions to this new exiting structure.

