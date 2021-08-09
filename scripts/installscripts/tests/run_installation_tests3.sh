#!/usr/bin/env bash

# Install Phoniebox and test it
# Used e.g. for tests on Docker

# Objective: Test installation with script using a configuration with mopidy

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
# y spotify with myuser, mypassword, myclient_id, myclient_secret
# y configure mpd
# y audio default location
# y config gpio
# n no RFID registration
# n No reboot

# TODO check, how this behaves on branches other than develop
GIT_BRANCH=develop bash ./scripts/installscripts/buster-install-default.sh <<< $'y\nn\n\ny\n\ny\nmyuser\nmypassword\nmyclient_id\nmyclient_secret\n\ny\n\ny\n\ny\n\ny\nn\nn\n'

# Test installation
./scripts/installscripts/tests/test_installation.sh
