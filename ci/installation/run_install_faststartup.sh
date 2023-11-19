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
# y - use static ip
# y - deactivate ipv6
# n - setup autohotspot
# y - deactivate bluetooth
# y - disable on-chip audio
# - - mpd overwrite config (only with existing installation)
# n - setup rfid reader
# n - setup samba
# n - build local WebApp
# - - setup kiosk mode (only with WebApp = y)
# - - install node (only with WebApp = y)
# n - reboot

"$local_install_script_path"/install-jukebox.sh <<< 'y
y
y
n
y
y
n
n
n
n
'
