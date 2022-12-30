# Jukebox Installation Routines

## Logging - Bash Script output rules

```bash
Output to both console and logfile:     "$ command | tee /dev/fd/3"
Output to console only                  "$ command 1>&3"
Output to logfile only:                 "$ command"
No output to both console and logfile:  "$ command > /dev/null"
```

[Learn more about bash script outputs](https://stackoverflow.com/questions/18460186/writing-outputs-to-log-file-and-console)

## Quick Installation

Note: Replace the branch in this command to be the one you like to install depending on your needs. Release branch is preset.

```bash
cd; bash <(wget -qO- https://raw.githubusercontent.com/MiczFlor/RPi-Jukebox-RFID/future3/main/installation/install-jukebox.sh)
```
