#!/usr/bin/env bash

# Install Phoniebox and test it
# Used e.g. for tests on Docker

# Objective: Test installation with script using a simple configuration

# Print current path
echo $PWD

# Preparations
# Skip interactive Samba WINS config dialog
echo "samba-common samba-common/dhcp boolean false" | sudo debconf-set-selections
# No interactive frontend
export DEBIAN_FRONTEND=noninteractive

# Run installation (in interactive mode)
# y confirm interactive
# n dont configure wifi
# y Headphone as iface
# n no spotify
# y configure mpd
# y audio default location
# y config gpio 
# n no RFID registration
# n No reboot

bash ./scripts/installscripts/buster-install-default.sh <<< $'y\nn\n\ny\n\nn\n\ny\n\ny\n\ny\n\ny\nn\nn\n'
INSTALLATION_EXITCODE=$?

# Test installation
./scripts/installscripts/tests/test_installation.sh $INSTALLATION_EXITCODE
