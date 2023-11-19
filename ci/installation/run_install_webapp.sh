#!/usr/bin/env bash

# Install Phoniebox and test it
# Used e.g. for tests on Docker

# Objective: Test installation with script using a simple configuration

local_install_script_path="${INSTALL_SCRIPT_PATH:-./../../installation/}"
local_install_script_path="${local_install_script_path%/}"

# Preparations
# No interactive frontend
export DEBIAN_FRONTEND=noninteractive
echo 'debconf debconf/frontend select Noninteractive' | sudo debconf-set-selections

# Run installation (in interactive mode)
# y - start setup
# n - use static ip
# n - deactivate ipv6
# n - setup autohotspot
# n - deactivate bluetooth
# n - disable on-chip audio
# - - mpd overwrite config (only with existing installation)
# n - setup rfid reader
# n - setup samba
# y - build local WebApp
# y - setup kiosk mode
# y - install node
# n - reboot

"$local_install_script_path"/install-jukebox.sh <<< 'y
n
n
n
n
n
n
n
y
y
y
n
'
