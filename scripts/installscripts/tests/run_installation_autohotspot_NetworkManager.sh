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
# n configure wifi (extra ENTER)
# y configure autohotspot
# n use autohotspot default config
#   y use custom data (extra ENTER)
# y use default audio iface (extra ENTER)
# n spotify (extra ENTER)
# y audio default location (extra ENTER)
# y config gpio (extra ENTER)
# y start installation
# n RFID registration
# n reboot
export CI_TEST_DHCPCD="false"
export CI_TEST_NETWORKMANAGER="true"
./../install-jukebox.sh <<< 'y
n

y
n
a!b"c§d$e%f&g/h(i)j=k?l´m`n²o³p{q[r]s}t\u+v*w~x#y'\''z01234
DE
ß,ä;ö.ü:Ä-Ö_Ü 1@2€3^4°5|6$7&8/9\0
192.168.100.2
y

y

n

y

y

y
n
n
'
INSTALLATION_EXITCODE=$?

# Test installation
./test_installation.sh $INSTALLATION_EXITCODE
