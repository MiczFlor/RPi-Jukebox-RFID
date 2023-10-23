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
# y confirm interactive mode
# n dont configure wifi (extra ENTER)
# y Headphone as iface (extra ENTER)
# y spotify with myuser, mypassword, myclient_id, myclient_secret
# y swapfile creation (extra ENTER)
# y configure mpd (extra ENTER)
# y audio default location (extra ENTER)
# y config gpio (extra ENTER)
# n start installation

# TODO check, how this behaves on branches other than develop
GIT_BRANCH=develop bash ./scripts/installscripts/buster-install-default.sh <<< "y
n

y

y
myuser
mypassword
myclient_id
myclient_secret
y

y

y

y
n
n
"

# Test installation
./scripts/installscripts/tests/test_installation.sh
