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

"${LOCAL_INSTALL_SCRIPT_PATH}/install-jukebox.sh" <<< 'y
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
