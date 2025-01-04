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
# n configure wifi (extra ENTER)
# n configure autohotspot (extra ENTER)
# y use default audio iface (extra ENTER)
# y spotify with myuser, mypassword, myclient_id, myclient_secret (extra ENTER)
# y audio default location (extra ENTER)
# y config gpio (extra ENTER)
# y start installation
# n RFID registration
# n reboot

./../install-jukebox.sh <<< 'y
n

n

y

y
a!b"c§d$e%f&g/h(i)j=k?l´m`n²o³p{q[r]s}t\u+v*w~x#y'\''zß,ä;ö.ü:Ä-Ö_Ü 1@2€3^4°5|67890
myclient+SECRET/0123456789=

y

y

y
n
n
'
INSTALLATION_EXITCODE=$?

# Test installation
./test_installation.sh $INSTALLATION_EXITCODE
