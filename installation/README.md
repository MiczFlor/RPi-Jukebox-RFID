# Jukebox Installation Routines

## Logging - Bash Script output rules

```
Output to both console and logfile:     "$ command | tee /dev/fd/3"
Output to console only                  "$ command 1>&3"
Output to logfile only:                 "$ command"
No output to both console and logfile:  "$ command > /dev/null"
```
