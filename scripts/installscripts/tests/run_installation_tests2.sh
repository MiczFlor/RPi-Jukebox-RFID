#!/usr/bin/env bash

# Install Phoniebox and test it
# Used e.g. for tests on Docker

# Objective: Test installation with script using a RC522 reader

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
# y PCM as iface
# n no spotify
# y configure mpd
# y audio default location
# y RFID registration
# 2 use RC522 reader
# yes, reader is connected
# n No reboot

# TODO check, how this behaves on branches other than develop
GIT_BRANCH=develop bash ./scripts/installscripts/buster-install-default.sh <<< $'y\nn\n\ny\n\nn\n\ny\n\ny\n\ny\ny\n2\ny\nn\n'

# Rest installation
./scripts/installscripts/tests/test_installation.sh
