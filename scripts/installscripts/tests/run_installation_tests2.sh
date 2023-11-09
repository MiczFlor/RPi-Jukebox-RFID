#!/usr/bin/env bash

# Install Phoniebox and test it
# Used e.g. for tests on Docker

# Objective: Test installation with script using a RC522 reader

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
# y PCM as iface
# n no spotify
# y configure mpd
# y audio default location
# y use gpio
# y RFID registration
# 2 use RC522 reader
# yes, reader is connected
# n No reboot

./../buster-install-default.sh <<< $'y\nn\n\nn\n\ny\n\nn\n\ny\n\ny\n\ny\n\ny\ny\n2\ny\nn\n'
INSTALLATION_EXITCODE=$?

# Test installation
./test_installation.sh $INSTALLATION_EXITCODE
