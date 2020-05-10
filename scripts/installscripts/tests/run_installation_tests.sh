#!/usr/bin/env bash

# Install Phoniebox and test it
# Used e.g. for tests on Docker

# print current path
echo $PWD

# run installation (in interactive mode)
# y confirm interactive
# n dont configure wifi
# y PCM as iface
# n no spotify
# y configure mpd
# y audio default location
# y start installation
./scripts/installscripts/buster-install-default.sh <<< $'y\nn\ny\nn\ny\ny\ny\n'

# test installation
./scripts/installscripts/tests/test_installation.sh
