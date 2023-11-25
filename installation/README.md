# Jukebox Installation Routines

## Logging - Bash Script output rules

```bash
Output to both console and logfile:     "$ command | tee /dev/fd/3"
Output to console only                  "$ command 1>&3"
Output to logfile only:                 "$ command"
No output to both console and logfile:  "$ command > /dev/null"
```

[Learn more about bash script outputs](https://stackoverflow.com/questions/18460186/writing-outputs-to-log-file-and-console)

## Installation

[Install Phoniebox software](../documentation/builders/installation.md#install-phoniebox-software)
