#!/usr/bin/env bash

# Install Phoniebox and test it
# Used e.g. for tests on Docker

# Objective: Test installation with script using a configuration with mopidy

# Print current path
echo $PWD

# Preparations
# No interactive frontend
export DEBIAN_FRONTEND=noninteractive
echo 'debconf debconf/frontend select Noninteractive' | sudo debconf-set-selections

# Run installation (in interactive mode)
# y confirm interactive
# n dont configure wifi
# n dont configure autohotspot
# y Headphone as iface
# y spotify with myuser, mypassword, myclient_id, myclient_secret
# y configure mpd
# y audio default location
# y config gpio
# n no RFID registration
# n No reboot

./../install-jukebox.sh <<< $'y\nn\n\nn\n\ny\n\ny\nmyuser\nmypassword\nmyclient_id\nmyclient_secret\n\ny\n\ny\n\ny\n\ny\nn\nn\n'
INSTALLATION_EXITCODE=$?

# Test installation
./test_installation.sh $INSTALLATION_EXITCODE
