---
name: bug report
about: use this template to report bugs
title: "\U0001F41B | BUG SUMMARY"
labels: bug, needs triage
---

## Bug

### What I did

<!--
i.e. `I installed the raspberry pi with above mentioned buster image and ran the installer script`
-->

### What happened

<!--
i.e. `During the first run of 'apt-get install' an error was shown: 'E: Broken packages'`
-->

### I expected this to happen

<!--
i.e. `I would have expected that this command would magically fix itself when it encounters and error.`
-->

### Further information that might help

<!--
Please post here the output of 'tail -n 500 /var/log/syslog' or 'journalctl -u mopidy' ( Spotify edition only)

i.e. `find logfiles at https://paste.ubuntu.com/p/cRS7qM8ZmP/`
-->


## Software

### Base image and version

<!--
i.e. `2019-09-26-raspbian-buster-lite.img`

Otherwise the output of `cat /etc/os-release`
-->

### Branch / Release

<!--
i.e. `master`

the following command will help with that
`cd /home/pi/RPi-Jukebox-RFID/ && git status | head -2`
-->

### Installscript

<!--
i.e. `scripts/installscripts/buster-install-default.sh`
-->


## Hardware

### RaspberryPi version

<!--
i.e. `3 B+`

Can be obtained by executing `sudo cat /sys/firmware/devicetree/base/model` on the RaspberryPi
-->

### RFID Reader

<!--
i.e. `16c0:27db HXGCoLtd Keyboard`

Can be found in the output of `sudo lsusb -v` when it is connected via USB.
-->

### Soundcard

<!--
i.e. `0d8c:0014 C-Media Electronics, Inc. Audio Adapter (Unitek Y-247A)`

Can be found in the output of `sudo lsusb -v` when it is connected via USB.
-->

### Other notable hardware

<!--
i.e. post your GPIO pin settings from `RPi-Jukebox-RFID/scripts/gpio-buttons.py`:
```
GPIO Buttons:
    volU = Button(22,pull_up=True,hold_time=0.3,hold_repeat=True)
    volD = Button(27,pull_up=True,hold_time=0.3,hold_repeat=True)
    frwd = Button(17,pull_up=True)
    prev = Button(24,pull_up=True)
    halt = Button(23,pull_up=True)
```
-->
