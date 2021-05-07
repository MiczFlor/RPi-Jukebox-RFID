This Branch is an attempt to realize elements from the discussion which took place in https://github.com/MiczFlor/RPi-Jukebox-RFID/discussions/1329

This is the first attempt to a new structure, many things here are untested and error prone. This is still in the phase of orientation and proof of concept with trails and experiments in many directions which all have to be understood as base for discussion.

In order to Focus on the actual topics many non needed/active items in this branch have been deleted. This doesn't mean existing parts are aboselte, things will be integrated step by step.

#### These are the Fundamental Design Goals:

- better maintainability
- clear strategy on architecture
- higher performance especially on lower end Hardware

#### To achieve this, the current direction is:

- avoid shell script invocation during runtime
- establish a socket based API 
- re-implement the core functionality in python

### What has been realized so far:

Running Player Functionality (Landing Page of WebUI) as a Python based rewrite of the Backend based on a socked API realized with ZMQ (Zero message Queue).

The work has taken place in the Components Folder, which has been renamed to Phoniebox since most of the existing Python code was located there. The Folder is structured as a Python Package, including all former components, mainly for the Reason of faster development right now.

### Architecture
The Fundamental Architecture looks like:

<img src="./docs/architecture.svg">


## PhonieboxDaemon:


### PhonieboxDaemon.py
This is the Entry point of this Implementation

This Daemon is so far:

- Playing Startup sound
- Reading Status and Database Files
- Instantiating Phoniebox Objects (Volume, Player, System Control)
- Instantiating and Starting RFID Reader as thread
- \##Instantiating and Starting GPIO Control
- Running the RPC Server (API)

_Next Steps here:_

- [X] reading of Config File in order to allow distributed development
- [ ] Refactoring as class in order to allow the exit functions to take over more tasks
- [ ] Add Logger ?
- [X] Add Command Line Interface to pass config etc. (e.g to be started by systemd)

### rpc/PhoniboxRpcServer.py

This Server is ZMQ based API, which takes a dictionary of control objects (classes) as argument. 
Each Method of the passed classes will be made available to the API

### rpc/PhoniboxRpcClient.py

Module which is intended to be included by other python Control Class in order to access the API


### PhoniboxNVManager.py

This is an Non Volatile Memory Manager. The attempt here is to reduce File IO writes, by keeping runtime Information in the RAM (a dictionary) and store them to Disk on Exit.

### PhoniboxVolume.py

ALSA Volume Control, utilizing pyalsaaudio
hard-coded ALSA Volume Control 

_Next Steps here:_

- [ ] allow Card and Interface configuration

### player/PhoniboxPlayerMPD.py

Core Player Function, Controls MPD (via python-mpd2)
Thsi si where most of the former Rsume Play and Playout Controls.sh went into

_Next Steps here:_

- [ ] Implement Resume Functionality
- [ ] Reduce / Organize Json Output  of playerstatus to what is really needed by the WebUI
- [ ] Switch mpd control to asyncio in order to be independent of WebUI Polling for actual  mpd status

## cli_client
command line access to the Daemon API,
This should be a very lightweight and fast interface-tool with nearly no further dependencies.

_Next Steps here:_

- [ ] Define and Implement Output Format which can be easily treated in a shell



## WebUI

Even there are many changes in the WebUI it has been keept as it was as much as possible.
The changes are mainly in order to interface with the new ZMQ aproach

### htdocs/api/PhonieboxRpcClient.php
this is the PHP Version of the RpcClient to allow fast and lightweight API access

_Next Steps here:_

- [ ] get all configuration needed from the Daemon via the API instead of setting files
- [ ] reduce the still 109 exec calls ....
- [ ] evaluate jszmq or zeromq.js as option to directly interface the API via js (https://github.com/zeromq)






