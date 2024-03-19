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
# y confirm interactive mode
# y configure wifi
# y use wifi data (extra ENTER)
# n configure autohotspot
# - use autohotspot default config (extra ENTER)
# y use default audio iface (extra ENTER)
# n spotify (extra ENTER)
# n configure mpd (extra ENTER)
# y audio default location (extra ENTER)
# y config gpio (extra ENTER)
# y start installation
# n RFID registration
# n reboot
export CI_TEST_DHCPCD="true"
export CI_TEST_NETWORKMANAGER="false"
./../install-jukebox.sh <<< "y
y
TestWifi
DE
TestWifiPW
192.168.100.2
192.168.100.1
y

n

y

n

n

y

y

y
n
n
"
INSTALLATION_EXITCODE=$?

# Test installation
./test_installation.sh $INSTALLATION_EXITCODE
