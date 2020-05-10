#!/usr/bin/env bash

# Install Phoniebox and test it
# Used e.g. for tests on Docker

# Print current path
echo $PWD

# Preparations
# Skip interactive Samba WINS config dialog
echo "samba-common samba-common/dhcp boolean false" | sudo debconf-set-selections

# Run installation (in interactive mode)
# y confirm interactive
# n dont configure wifi
# y PCM as iface
# n no spotify
# y configure mpd
# y audio default location
# y start installation
./scripts/installscripts/buster-install-default.sh <<< $'y\nn\ny\nn\ny\ny\ny\n'

# Rest installation
./scripts/installscripts/tests/test_installation.sh
