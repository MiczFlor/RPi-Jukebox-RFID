---
name: bug report
about: use this template to report bugs
title: ":bug: [BUG SUMMARY]"
labels: bug, needs triage
assignees: MiczFlor
---

## Hardware

### RaspberryPi version

i.e. `3 B+`

### RFID Reader

i.e. `16c0:27db HXGCoLtd Keyboard`

### Soundcard

i.e. `0d8c:0014 C-Media Electronics, Inc. Audio Adapter (Unitek Y-247A)`

### Other notable hardware

i.e.:
```
GPIO Buttons:
    volU = Button(22,pull_up=True,hold_time=0.3,hold_repeat=True)
    volD = Button(27,pull_up=True,hold_time=0.3,hold_repeat=True)
    frwd = Button(17,pull_up=True)
    prev = Button(24,pull_up=True)
    halt = Button(23,pull_up=True)
```

## Software

### Base image and version

i.e. `2019-09-26-raspbian-buster-lite.img`

### Branch / Release

i.e. `master`

### Installscript

i.e. `scripts/installscripts/buster-install-default.sh`


## Bug

### What I did

i.e. `I installed the raspberry pi with above mentioned buster image and ran the installer script`

### What happened

i.e. `During the first run of 'apt-get install' an error was shown: 'E: Broken packages'`

### I expected this to happen

i.e. `I would have expected that this command would magically fix itself when it encounters and error.`

### Further information that might help

i.e. `find logfiles at https://paste.ubuntu.com/p/cRS7qM8ZmP/`
