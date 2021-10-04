.. |[X]| unicode:: 0x2611
.. |[ ]| unicode:: 0x2610

Feature Status
****************

In a nutshell
------------------

This is where we are in a nutshell: Playing music from local folders via RFID trigger. Also the new WebUI is there
to control the Jukebox.

The are a few things that are specifically not integrated yet: GPIOs, playing streams or podcast, Spotify.

In more detail
------------------

Here is the currently implemented feature list in more detail. It also shows some of the holes. However the list
is not complete in terms of planned features, but probably reflects more of where work is currently being put into.

General
^^^^^^^^^^

* |[ ]| Method to change configuration through WebUI
  * The difficulty lies bringing the running Jukebox to accept the changes
* |[ ]| Strategy to post config changes via PubSub

    * e.g. volume change is posted repeatedly with status
    * but what about set_max_volume, is shutdown timer active?

* |[ ]| Clean up of surplus files
* |[X]| Host interface (shutdown, reboot)
* |[X]| Temperature getter / publisher
* |[ ]| is_throttled getter / publisher
* |[X]| Version number getter / Git Hash

  * |[ ]| Log and publish this!

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

* |[ ]| /shared/references: plugin_reference / rpc commands reference / card actions reference / card db summary

Via RPC
^^^^^^^^^^

  * |[X]| List of loaded / failed plugins
  * |[X]| card action reference
  * |[X]| Help command (available commands)

      * which basically is a plugin reference

Config handler
^^^^^^^^^^^^^^^^^^

* |[ ]| While saving config to disk: local file change detection
* |[ ]| cfghandler creates setndefault() at arbitrary depth

0MQ Publisher
^^^^^^^^^^^^^^

* |[X]| Last Value Cache
* |[X]| Subscriber detection and initial status update
* |[X]| Port configuration option (WS und/oder TCP)
* |[ ]| Callback registration option for plugin on topic send

WebUI
^^^^^^^^^^

* |[X]| Playback Control
* |[X]| Cover Art
* |[X]| Register cards / Delete Card
* |[X]| Shutdown button
* |[ ]| Settings configuration page

Playback
^^^^^^^^^^

* |[ ]| Playlist generator (in work)

    * |[ ]| Local folders

        * |[ ]| Non-recursive folder play
        * |[ ]| Recursive folder play

    * |[ ]| Podcast
    * |[ ]| Livestreams
    * |[ ]| NEW: Playback of m3u playlists (e.g. folder.m3u) ?

* |[ ]| Folder configuration `Reference <https://github.com/MiczFlor/RPi-Jukebox-RFID/wiki/MANUAL#manage-playout-behaviour>`_

  * |[ ]| Resume: Save and restore position (how interact with shuffle?)
  * |[ ]| Single: Enable mpc single
  * |[ ]| Shuffle: Enable mpc random (not shuffle)

        * Rename to random, as this is mpc random

  * |[ ]| Loop: Loop playlist

MPD Player
^^^^^^^^^^

* |[ ]| Thread safety for status information / configuration
* |[ ]| Differential status post
* |[ ]| Second swipe option setter via RPC
* |[ ]| Volume publisher for ALSA / MPD switchable

    * |[ ]| ALSA volume check with select.poll()

* |[ ]| Before every music lib update, player should check user rights (not only after start-up)

RFID
^^^^^^^^^^

* |[X]| Test with Reader disabled
* |[X]| Start-up behaviour with un-configured Reader
* |[X]| Command card -> is now parameter ignore_same_id_delay
* |[X]| Revised RFID reader user-query setup script

  * |[ ]| Ask for place option

* |[ ]| Enable config flag ?
* |[X]| Place not swipe / Timer thread

    * |[X]| Configurable card removal action

* |[ ]| Readers support

    * |[X]| USB (e.g. Neuftech)
    * |[X]| RDM6300
    * |[ ]| MFRC522
    * |[ ]| RC532
    * |[ ]| PC/SC Cards
    * |[X]| Multi-reader support
    * |[X]| GUI Fake Reader for Development

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
    * |[ ]| Base quick select on yaml file

Cards
^^^^^^^^^^

* |[ ]| Write a simplified card summary to

    * |[ ]| file
    * |[X]| RPC

* |[ ]| Card assignment function for WebUI

    * |[X]| Via Quick select
    * |[ ]| Full custom RPC call

* |[X]| Remove card

Timer
^^^^^^^^^^

* |[ ]| Idle timer
* |[X]| Shutdown timer
* |[X]| Play stop timer
* |[X]| Shutdown timer volume reduction

    * Decreases volume every x min until zero, then shuts down
    * Needs to be cancelable

* |[X]| Publish mechanism of timer status
* |[ ]| Make timer settings persistent
* |[ ]| Change multitimer function call interface such that Endless timer etc do not pass the `iteration` kwarg


Installation
^^^^^^^^^^^^^^^

* |[X]| Single call installation script
* |[ ]| Query for settings vs. automatic version, e.g.

    * before overwriting MPD config (i.e. for re-installs)
    * static IP
    * ALSA Mixer interface

* |[ ]| IPQoS in SSH config
* |[ ]| Separate static IP and IPv6 disable


Volume
^^^^^^^^^^

* |[ ]| Min/Max Volume
* |[X]| Jingle playback volume as fixed value in config
* |[X]| Default volume setting after boot-up
* |[X]| MPD volume control service

GPIO
^^^^^^^^^^

* |[ ]| Everything needs porting

    * Function call routines need replacing to do RPC Calls
    * Configuration format probably best changed to YAML

* |[ ]| Status LED probably needs re-writing to benefit fully from plugin structure
* |[ ]| USB Buttons: It's a different category as it works similar to the RFID cards
* |[ ]| Port rfid pin action to GPIO as a general pin service for all plugins

WLAN
^^^^^^^^^^

* |[ ]| Ad-hoc WLAN Hot spot
* |[ ]| IP address read-out

Spotify
^^^^^^^^^^

* |[ ]| Everything

Others
^^^^^^^^^^

* |[ ]| Bluetooth sink toggle
* |[ ]| MQTT
* |[ ]| Record and Playback using a Mic

Start-up stuff
^^^^^^^^^^^^^^^^

* |[X]| check music folder rights
* |[X]| mpc update / (mpc rescan)
* |[ ]| sudo iwconfig wlan0 power off (need to be done after every restart)
* |[ ]| Optional power down HDMI circuits: /usr/bin/tvservice -o

Debug Tools
^^^^^^^^^^^^^^

* |[X]| Publishing Sniffer

    * |[ ]| Update mode vs linear mode ?

* |[X]| RPC command line client

    * with tab-completion and history


Documentation
^^^^^^^^^^^^^^

* |[X]| Sphinx / Restructured Text tool flow
* |[ ]| What is the Phoniebox
* |[ ]| Artifacts: Generate artifacts from plugins, quick actions, card db on command line switch
* |[ ]| How to: Write a plugin
