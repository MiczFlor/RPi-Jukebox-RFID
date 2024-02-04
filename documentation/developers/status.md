# Feature Status

**This is where we are in a nutshell:** Playing music from local folders via RFID trigger. We also built a new WebUI to control the Jukebox from a browser.

There are a few things that are specifically not integrated yet: playing streams, podcasts, or Spotify.

In the following is the currently implemented feature list in more detail. It also shows some of the shortcomings. However, the list is _not complete in terms of planned features_, but probably _reflects more of where work is currently being put into_.

**For new contributors:** If you want to port a feature from version 2.X or implement a new feature, contact us. Open an issue or join us in the chat room. You may pick topics marked as open below, but also any other topic missing in the list below. As mentioned, that list is not complete in terms of open features. Check the [Contribution guide](../../CONTRIBUTING.md).

Topics marked _in progress_ are already in the process of implementation by community members.

## Table of Contents

- [Feature Status](#feature-status)
  - [Table of Contents](#table-of-contents)
  - [Jukebox Core App](#jukebox-core-app)
    - [Base](#base)
    - [Via RPC](#via-rpc)
    - [Config handler](#config-handler)
    - [ZMQ Publisher](#zmq-publisher)
    - [Playback](#playback)
    - [MPD Player](#mpd-player)
    - [RFID](#rfid)
    - [Cards](#cards)
    - [Timer](#timer)
    - [Volume](#volume)
    - [GPIO](#gpio)
    - [WLAN](#wlan)
    - [Spotify](#spotify)
    - [Others](#others)
    - [Start-up stuff](#start-up-stuff)
  - [Debug Tools](#debug-tools)
  - [WebUI](#webui)
  - [Installation Procedure](#installation-procedure)
  - [Documentation](#documentation)

## Jukebox Core App

### Base

- [x] Clean up surplus files
- [x] Host interface (shutdown, reboot)
- [x] Temperature getter
  - [x] Timer + Publisher
- [x] RPi is_throttled getter
  - [x] Decode hex value to readable string (check version 2.x mqtt as reference?)
  - [x] Timer + Publisher
- [x] Git hash log information
  - [x] Log and publish this!
- [x] Version number getter (Version number should be stored in a python file)
  - [x] Log and publish this
- [x] Exit via RPC
- [x] Service restart via RPC
  - [x] Check if really running as a service
- [x] Storage space getter / publisher (shutil.disk_usage)
- [x] Getter for error logs to show in WebUI
  - Get file location from FileHandlers (files may be stale!)
  - Logger might be disabled or not connected
- [ ] Enable/Disable debug logging from RPC
- [x] Publisher of errors (specialized logger handler)
  - This is a configurable logger handler in logger.yaml
- [x] Basic Logging Config should enable Publisher stream handler
- [ ] Disable Console Stream Handler (or set to warning) when running as a service
- [x] Log & publish start time
- [ ] Method to change configuration through WebUI
  - The difficulty lies in bringing the running Jukebox to accept the changes. There probably won't be a catch-all solution but rather a custom implementation for a select few features
- [x] Strategy to post config changes via PubSub: Must be taken care of by the setter function modifying the property

### Via RPC

- [x] List of loaded / failed plugins
- [x] card action reference
- [x] Help command (available commands)
  - which basically is a plugin reference
- [x] Simplified alias definitions for often used RPC commands (for RFID, GPIO, etc)
  - [ ] Port all previous commands
  - [x] Reference file write-out: now also included in Sphinx documentation
  - [ ] Export available alias definitions to RPC
  - [ ] Base quick select on yaml file (_in progress_)
    - or write a yaml file as an artifact that contains all the meta information about the functions as well?
    - or include a `get_signature` function that returns the meta information for a given alias

### Config handler

- [x] While saving config to disk: local file change detection
- [x] cfghandler creates setndefault() at an arbitrary depth

### ZMQ Publisher

- [x] Last Value Cache
- [x] Subscriber detection and initial status update
- [x] Port configuration option (WS and/or TCP)
- [ ] Callback registration option for plugin on topic send
  - How to interact with threads?

### Playback

- [x] Playlist generator
  - [x] Local folders
    - [x] Non-recursive folder play
    - [x] Recursive folder play
  - [x] Podcast
  - [x] Livestreams
  - [x] NEW: Playback of m3u playlists (e.g., folder.m3u) ?

- [ ] Folder configuration (_in progress_)
  - [ ] [Reference](https://github.com/MiczFlor/RPi-Jukebox-RFID/wiki/MANUAL#manage-playout-behaviour)
  - [ ] Resume: Save and restore position (how interact with shuffle?)
  - [ ] Repeat Playlist
  - [ ] Repeat Song
  - [ ] Shuffle

### MPD Player

- [ ] Thread safety for status information / configuration (_in progress_)
- [ ] Differential status post (_in progress_)
- [ ] Second swipe option setter via RPC (_in progress_)
- [ ] Before every music lib update, player should check user rights (not only after start-up)

### RFID

- [x] Test with Reader disabled
- [x] Start-up behavior with un-configured Reader
- [x] Command card -> is now parameter ignore_same_id_delay
- [x] Revised RFID reader user-query setup script
  - [ ] Ask for place option
- [ ] Enable config flag ?
- [x] Place not swipe / Timer thread
  - [x] Configurable card removal action
- [x] Readers support
  - [x] USB (e.g., Neuftech)
  - [x] RDM6300
  - [x] MFRC522
  - [x] RC532
  - [x] Multi-reader support
  - [x] GUI Fake Reader for Development
  - [ ] PC/SC Cards (what actually is this?)
- [x] Publish RFID Card ID via PubSub
  - Needs to be thread safe
- [x] Card reference IF via RPC
- [x] Second Swipe Options -> must be part of player control (partially broken at the moment)
  - Freely configurable with an RPC call
  - Ignore (nothing)
  - Toggle Pause/Play
  - Skip to the next track
  - Re-start playlist

### Cards

- [ ] Write a simplified card summary to
  - [ ] file
  - [x] RPC
- [ ] Card assignment function for WebUI
  - [x] Via RPC command alias definitions
  - [ ] Full custom RPC call
- [x] Remove card

### Timer

- [x] Shutdown timer
- [x] Play stop timer
- [x] Shutdown timer volume reduction
  - Decreases volume every x min until zero, then shuts down
  - Needs to be cancelable
- [x] Publish mechanism of timer status
- [x] Change multitimer function call interface such that endless timer etc. won't pass the `iteration` kwarg
- [ ] Make timer settings persistent
- [ ] Idle timer
  - This needs clearer specification: Idle is when no music is playing and no user interaction is taking place
  - i.e., needs information from RPC AND from player status. Let's do this when we see a little clearer about Spotify

### Volume

- [x] Jingle playback volume as a fixed value in config
- [x] Default volume setting after boot-up
- [x] Max Volume
- [x] PulseAudio integration with event handler
- [x] Bluetooth support
- [x] Automatic audio sink toggle
  - [ ] Callbacks for audio sink change

### GPIO

- [x] All done! Read the docs at [GPIO Recipes](#builders/gpioz:GPIO Recipes)!
- [ ] USB Buttons: It's a different category as it works similar to the RFID cards (in progress)

### WLAN

- [x] Ad-hoc WLAN Hotspot
- [x] IP address read-out

### Spotify

- [ ] Everything

### Others

- [ ] MQTT
- [ ] Record and Playback using a Mic
- [ ] Dot Matrix Displays

### Start-up stuff

- [x] check music folder permissions
- [x] mpc update / (mpc rescan)
- [x] sudo iwconfig wlan0 power off (need to be done after every restart)
- [x] Optional power down HDMI circuits: /usr/bin/tvservice -o

## Debug Tools

- [x] Publishing Sniffer
  - [ ] Update mode vs. linear mode?
- [x] RPC command line client
  - [x] with tab-completion and history

## WebUI

- [x] Playback Control
- [x] Cover Art
- [x] Register cards / Delete cards
- [x] Shutdown button
- [ ] Settings configuration page
- [ ] System information page
  - [ ] Configure (one or multiple) WLANs
  - [x] Enable/Disable Auto-Hotspot
- [x] `run_npm_build` script
  - [x] Must consider `export NODE_OPTIONS=--max-old-space-size=512`
- [ ] Upload audio files via WebUI <https://github.com/MiczFlor/RPi-Jukebox-RFID/issues/2138>

## Installation Procedure

- [x] Single call installation script
- [x] Query for settings vs. automatic version
- [x] IPQoS in SSH config
- [x] Separate static IP and IPv6 disable
- [ ] For all system config file changes, check prior to modification if modification already exists

## Documentation

- [x] Sphinx / Restructured Text tool flow
- [ ] What is the Phoniebox
- [x] Artifacts: Generate artifacts (on command line switch only) for
  - [x] loaded plugins and rpc command aliases (to sphinx and shared/artifacts)
  - [x] rpc command aliases (to sphinx and shared/artifacts)
- [ ] How to: Write a plugin
