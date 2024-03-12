#!/usr/bin/env bash

# Install Phoniebox and test it
# Used e.g. for tests on Docker

# Objective: Test installation with script using a simple configuration

# Print current path
echo $PWD

# Preparations
# No interactive frontend
export DEBIAN_FRONTEND=noninteractive
echo 'debconf debconf/frontend select Noninteractive' | sudo debconf-set-selections

# Run installation (in interactive mode)
# y confirm interactive
# n configure wifi (extra ENTER)
# n configure autohotspot (extra ENTER)
# - use autohotspot default config
# y use default audio iface (extra ENTER)
# n spotify (extra ENTER)
# y configure mpd (extra ENTER)
# y audio default location (extra ENTER)
# y config gpio (extra ENTER)
# y start installation
# n RFID registration
# n reboot

./../install-jukebox.sh <<< "y
n

n

y

n

y

y

y

y
n
n
"
INSTALLATION_EXITCODE=$?

# Test installation
./test_installation.sh $INSTALLATION_EXITCODE
