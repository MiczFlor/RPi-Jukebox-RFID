# Jukebox Installation Routines

## Logging - Bash Script output rules

```
Output to both console and logfile:     "$ command | tee /dev/fd/3"
Output to console only                  "$ command 1>&3"
Output to logfile only:                 "$ command"
No output to both console and logfile:  "$ command > /dev/null"
```

## Quick Installation

Note: Replace the branch in this command to be the one you like to install depending on your needs. Release branch is preset.

```
cd; bash <(wget -qO- https://raw.githubusercontent.com/MiczFlor/RPi-Jukebox-RFID/future3/main/installation/install-jukebox.sh)
```