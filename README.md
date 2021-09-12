# RFID Jukebox Version 3 (aka future3) 

### What is this?
A complete re-write of the Jukebox

### Why?
- better maintainability
- clear architecture allowing easier add-on and new feature
- higher performance especially on lower end Hardware

### How?

- Jukebox core is a holistic Python3-only application 
    - Avoid shell script invocation during runtime wherever possible
- Establish a socket based API (using libzeromq) toward the WebUI
- Implement a Remote-Procedure-Call (RPC) Server through which all user function call pass  
- Implement a plugin-concept to dynamically load additional Python Module for easy extendability 
    - In conjunction with the RPC this is a neat way of allwing addional feature without having to touch the core all the time

### Where are we?

The initial proof-of-concept phase has been left behind and there already is quite some functionality available. 
This is still heavily in progress, but the WebUI and RFID-triggered playback of local files works.

Features/Files form the Version 2.X branch will only be copied/merged when they can be integrated and tested. 
If you don't find your v2.X contributions, it doesn't mean they are obsolete. Things will be integrated step by step.


## Feature Rollout Plan (aka To-Do List)

**General**
- [ ] Method to change configuration through WebUI
  - The difficulty lies bringing the running Jukebox to accept the changes
- [ ] Strategy to post config changes via PubSub
    - e.g. volume change is posted repeatedly with status
    - but what about set_max_volume, is shutdown timer active?
    
- [ ] Clean up of surplus files
- [X] Host interface (shutdown, reboot)
- [X] Temperature getter / publisher
- [ ] is_throttled getter / publisher
- [ ] Version number getter
- [ ] Exit through RPC
- [ ] Storage space getter / publisher (shutil.disk_usage)

**Config handler**
- [ ] While saving config to disk: local file change detection
- [ ] cfghandler creates setndefault() at arbitrary depth

**WebUI**
- [X] Playback Control
- [ ] Cover Art  
- [ ] Register cards
- [ ] Shutdown button 

**Playback**
- [ ] Playlist generator
    - [ ] Local folders
        - [ ] Non-recursive folder play
        - [ ] Recursive folder play
    - [ ] Podcast
    - [ ] Livestreams
    - [ ] NEW: Playback of m3u playlists (e.g. folder.m3u) ?
    
- [ ] Folder configuration [Reference](https://github.com/MiczFlor/RPi-Jukebox-RFID/wiki/MANUAL#manage-playout-behaviour)
  - [ ] Resume: Save and restore position (how interact with shuffle?) 
  - [ ] Single: Enable mpc single
  - [ ] Shuffle: Enable mpc random (not shuffle)
    - Rename to random, as this is mpc random
  - [ ] Loop: Loop playlist 

**RFID**
- [X] Test with Reader disabled 
- [X] Start-up behaviour with un-configured Reader
- [X] Command card -> is now parameter ignore_same_id_delay
- [X] Revised RFID reader user-query setup script
  - [ ] Ask for place option
- [ ] Enable config flag ?  
- [X] Place not swipe / Timer thread
    - [X] Configurable card removal action
- [ ] Readers support
    - [X] USB (e.g. Neuftech)
    - [X] RDM6300
    - [ ] MFRC522
    - [ ] RC532
    - [ ] PC/SC Cards
    - [X] Multi-reader support
    - [X] GUI Fake Reader for Development
- [ ] Publish RFID Card ID via PubSub
  - Needs to be thread safe
- [X] Second Swipe Options -> must be part of player control
    - Freely configurable with an RPC call
    - Ignore (nothing)
    - Toggle Pause/Play
    - Skip to next track
    - Re-start playlist
- [X] Simplified quick_select action shortcuts for often used card commands
    - [ ] Port all previous card commands
    - [X] Reference file write-out
      - [ ] Improve readability
    - [ ] Card reference IF via RPC (?)

**Timer**
- [ ] Idle timer
- [X] Shutdown timer
- [X] Play stop timer
- [X] Shutdown timer volume reduction
    - Decreases volume every x min until zero, then shuts down
    - Needs to be cancelable
- [ ] Publish mechanism of timer status    


**Installation**
- [X] Single call installation script
- [ ] Query for settings vs. automatic version, e.g.
    - before overwriting MPD config (i.e. for re-installs)
    - static IP
- [ ] IPQoS in SSH config   
- [ ] Separate static IP and IPv6 disable
    

**Volume**
- [ ] Min/Max Volume
- [X] Jingle playback volume as fixed value in config
- [X] Default volume setting after boot-up
- [X] MPD volume control service

**GPIO**
- [ ] Everything needs porting
  - Function call routines need replacing to do RPC Calls
  - Configuration format probably best changed to YAML  
- [ ] Status LED probably needs re-writing to benefit fully from plugin structure 
- [ ] USB Buttons

**WLAN**
- [ ] Ad-hoc WLAN Hot spot
- [ ] IP address read-out

**Spotify**
- [ ] Everything

**Others**
- [ ] Bluetooth sink toggle
- [ ] MQTT 
- [ ] Record and Playback using a Mic

**Start-up stuff**
- [X] check music folder rights
- [X] mpc update / (mpc rescan)
- [ ] sudo iwconfig wlan0 power off (need to be done after every restart)
- [ ] Optional power down HDMI circuits: /usr/bin/tvservice -o

### Architecture
The Fundamental Architecture looks like:

<img src="./docs/architecture.svg">



