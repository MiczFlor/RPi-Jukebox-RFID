#!/usr/bin/env bash

# Install Phoniebox and test it
# Used e.g. for tests on Docker

# Objective: Test installation with script using a simple configuration

SOURCE="${BASH_SOURCE[0]}"
SCRIPT_DIR="$(dirname "$SOURCE")"
LOCAL_INSTALL_SCRIPT_PATH="${INSTALL_SCRIPT_PATH:-${SCRIPT_DIR}/../../installation}"
LOCAL_INSTALL_SCRIPT_PATH="${LOCAL_INSTALL_SCRIPT_PATH%/}"

# Run installation (in interactive mode)
# y - start setup
# n - use static ip
# n - deactivate ipv6
# y - setup autohotspot
# n -   use custom password
# n - deactivate bluetooth
# n - disable on-chip audio
# - - mpd overwrite config (only with existing installation)
# n - setup rfid reader
# y - setup samba
# y - build local WebApp
# n - setup kiosk mode
# y - install node
# n - reboot

"${LOCAL_INSTALL_SCRIPT_PATH}/install-jukebox.sh" <<< 'y
n
n
y
n
n
n
n
y
y
n
y
n
'
