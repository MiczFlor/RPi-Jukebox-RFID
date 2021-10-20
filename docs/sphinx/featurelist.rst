.. |[X]| unicode:: 0x2611
.. |[ ]| unicode:: 0x2610

Feature Status
****************

**This is where we are in a nutshell:** Playing music from local folders via RFID trigger.
We also built a new WebUI to control the Jukebox from a browser.

The are a few things that are specifically not integrated yet: GPIOs, playing streams, podcasts or Spotify.

In the following is the currently implemented feature list in more detail. It also shows some of the holes.
However the list is *not complete in terms of planned features*,
but probably **reflects more of where work is currently being put into**.

**For new contributors:** If you want to port a feature from version 2.X or implement a new feature, contact us. Open an issue
or join us on in the chat room. You may pick topic marked as open below, but also any other topic missing in below list.
As mentioned, that list is not complete in terms of open features. Check the
`Contribution guide <https://github.com/MiczFlor/RPi-Jukebox-RFID/blob/future3/develop/CONTRIBUTING.md>`_.
Topics marked *in progress* are already in the process of implementation by community members.

.. contents::

Jukebox Core App
-------------------

Base
^^^^^^^^

* |[X]| Clean up of surplus files
* |[X]| Host interface (shutdown, reboot)
* |[X]| Temperature getter

    * |[X]| Timer + Publisher

* |[X]| RPi is_throttled getter

    * |[ ]| Decode hex value to readable string (check version 2.x mqtt as reference?)
    * |[ ]| Timer + Publisher

* |[X]| Git hash log information

  * |[ ]| Log and publish this!

* |[X]| Version number getter (Version number should be stored in a python file)

    * |[X]| Log and publish  this

* |[ ]| Exit via RPC
* |[ ]| Service restart via RPC

  * |[ ]| Check if really running as a service

* |[X]| Storage space getter / publisher (shutil.disk_usage)
* |[X]| Getter for error logs to show in WebUI

    * Get file location from FileHandlers (files may be stale!)
    * Logger might be disabled or not connected

* |[ ]| Enable/Disable debug logging from RPC
* |[X]| Publisher of errors (specialized logger handler)

    * This is a configurable logger handler in logger.yaml

* |[X]| Basic Logging Config should enable Publisher stream handler
* |[ ]| Disable Console Stream Handler (or set to warning) when running as a service
* |[X]| Log & publish start time
* |[ ]| /shared/references: plugin_reference / rpc commands reference / card actions reference / card db summary (*in progress*)
* |[ ]| Method to change configuration through WebUI

  * The difficulty lies bringing the running Jukebox to accept the changes. There probably won't be a catch all solution
    but rather a custom implementation for a select few features

* |[X]| Strategy to post config changes via PubSub: Must be taken care of by the setter function modifying the property


Via RPC
^^^^^^^^

* |[X]| List of loaded / failed plugins
* |[X]| card action reference
* |[X]| Help command (available commands)

  * which basically is a plugin reference

Config handler
^^^^^^^^^^^^^^^^^^^

* |[X]| While saving config to disk: local file change detection
* |[X]| cfghandler creates setndefault() at arbitrary depth

ZMQ Publisher
^^^^^^^^^^^^^^^^^

* |[X]| Last Value Cache
* |[X]| Subscriber detection and initial status update
* |[X]| Port configuration option (WS und/oder TCP)
* |[ ]| Callback registration option for plugin on topic send

    * How to interact with threading?

Playback
^^^^^^^^^^^^^^^^^

* |[X]| Playlist generator

    * |[X]| Local folders

        * |[X]| Non-recursive folder play
        * |[X]| Recursive folder play

    * |[X]| Podcast
    * |[X]| Livestreams
    * |[X]| NEW: Playback of m3u playlists (e.g. folder.m3u) ?

* |[ ]| Folder configuration  (*in progress*)

  * |[ ]| `Reference <https://github.com/MiczFlor/RPi-Jukebox-RFID/wiki/MANUAL#manage-playout-behaviour>`_
  * |[ ]| Resume: Save and restore position (how interact with shuffle?)
  * |[ ]| Single: Enable mpc single
  * |[ ]| Shuffle: Enable mpc random (not shuffle)

        * Rename to random, as this is mpc random

  * |[ ]| Loop: Loop playlist

MPD Player
^^^^^^^^^^^^^^^^^

* |[ ]| Thread safety for status information / configuration  (*in progress*)
* |[ ]| Differential status post  (*in progress*)
* |[ ]| Second swipe option setter via RPC  (*in progress*)
* |[ ]| Volume publisher for ALSA / MPD switchable  (*in progress*)

    * |[ ]| ALSA volume check with select.poll()  (*in progress*)

* |[ ]| Before every music lib update, player should check user rights (not only after start-up)

RFID
^^^^^^^^^^^^^^^^^

* |[X]| Test with Reader disabled
* |[X]| Start-up behaviour with un-configured Reader
* |[X]| Command card -> is now parameter ignore_same_id_delay
* |[X]| Revised RFID reader user-query setup script

  * |[ ]| Ask for place option

* |[ ]| Enable config flag ?
* |[X]| Place not swipe / Timer thread

    * |[X]| Configurable card removal action

* |[X]| Readers support (*in progress*)

    * |[X]| USB (e.g. Neuftech)
    * |[X]| RDM6300
    * |[X]| MFRC522
    * |[X]| RC532
    * |[X]| Multi-reader support
    * |[X]| GUI Fake Reader for Development
    * |[ ]| PC/SC Cards (what actually is this?)

* |[X]| Publish RFID Card ID via PubSub

    * Needs to be thread safe

* |[X]| Second Swipe Options -> must be part of player control

    * Freely configurable with an RPC call
    * Ignore (nothing)
    * Toggle Pause/Play
    * Skip to next track
    * Re-start playlist

* |[X]| Simplified quick_select action shortcuts for often used card commands

    * |[ ]| Port all previous card commands
    * |[X]| Reference file write-out

        * |[ ]| Improve readability

    * |[X]| Card reference IF via RPC (?)
    * |[ ]| Export available quick selects commands to RPC
    * |[ ]| Base quick select on yaml file (*in progress*)

Cards
^^^^^^^^^^^^^^^^^

* |[ ]| Write a simplified card summary to

    * |[ ]| file
    * |[X]| RPC

* |[ ]| Card assignment function for WebUI

    * |[X]| Via Quick select
    * |[ ]| Full custom RPC call

* |[X]| Remove card

Timer
^^^^^^^^^^^^^^^

* |[X]| Shutdown timer
* |[X]| Play stop timer
* |[X]| Shutdown timer volume reduction

    * Decreases volume every x min until zero, then shuts down
    * Needs to be cancelable

* |[X]| Publish mechanism of timer status
* |[X]| Change multitimer function call interface such that Endless timer etc do not pass the `iteration` kwarg
* |[ ]| Make timer settings persistent
* |[ ]| Idle timer

    * This needs clearer specification: Idle is when no music is playing and no user interaction si taking place
    * i.e. needs information from RPC AND from player status. Let's do this when we see a little clearer about Spotify



Volume
^^^^^^^^^^^^^^^^^

* |[X]| Jingle playback volume as fixed value in config
* |[X]| Default volume setting after boot-up
* |[X]| MPD volume control service
* |[X]| Min/Max Volume

    * |[ ]| Current state of Max Volume in webapp

* |[ ]| Error-safe mute/unmute for AlsaIF (not all sound cards support that)

GPIO
^^^^^^^^^^^^^^^^^

* |[ ]| Everything needs porting (*in progress*)

    * Function call routines need replacing to do RPC Calls
    * Configuration format probably best changed to YAML

* |[ ]| Status LED probably needs re-writing to benefit fully from plugin structure
* |[ ]| USB Buttons: It's a different category as it works similar to the RFID cards
* |[ ]| Port rfid pin action to GPIO as a general pin service for all plugins

WLAN
^^^^^^^^^^^^^^^^^

* |[ ]| Ad-hoc WLAN Hot spot
* |[ ]| IP address read-out

Spotify
^^^^^^^^^^^^^^^^^

* |[ ]| Everything

Others
^^^^^^^^^^^^^^^^^

* |[ ]| Bluetooth sink toggle
* |[ ]| MQTT
* |[ ]| Record and Playback using a Mic

Start-up stuff
^^^^^^^^^^^^^^^^^

* |[X]| check music folder rights
* |[X]| mpc update / (mpc rescan)
* |[X]| sudo iwconfig wlan0 power off (need to be done after every restart)

    * |[ ]| needs testing

* |[X]| Optional power down HDMI circuits: /usr/bin/tvservice -o

    * |[ ]| needs testing


Debug Tools
--------------

* |[X]| Publishing Sniffer

    * |[ ]| Update mode vs linear mode ?

* |[X]| RPC command line client

    * |[X]| with tab-completion and history


WebUI
--------------

* |[X]| Playback Control
* |[X]| Cover Art
* |[X]| Register cards / Delete Card
* |[X]| Shutdown button
* |[ ]| Settings configuration page
* |[ ]| System information page
* |[ ]| ``run_npm_build`` script

    * |[ ]| Must consider ``export NODE_OPTIONS=--max-old-space-size=512``


Installation Procedure
-----------------------

* |[X]| Single call installation script
* |[ ]| Query for settings vs. automatic version, e.g.

    * |[ ]| before overwriting MPD config (i.e. for re-installs)
    * |[ ]| static IP (DHCP or static IP from user input)
    * |[ ]| ALSA Mixer interface

* |[X]| IPQoS in SSH config
* |[X]| Separate static IP and IPv6 disable
* |[ ]| For all system config file changes, check prior to modification, if modification already exists


Documentation
--------------

* |[X]| Sphinx / Restructured Text tool flow
* |[ ]| What is the Phoniebox
* |[ ]| Artifacts: Generate artifacts from plugins, quick actions, card db on command line switch
* |[ ]| How to: Write a plugin
