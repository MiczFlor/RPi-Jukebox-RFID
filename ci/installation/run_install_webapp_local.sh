#!/usr/bin/env bash

# Install Phoniebox and test it
# Used e.g. for tests on Docker

# Objective:
# Test for the Web App (build locally) and dependent features path.

SOURCE="${BASH_SOURCE[0]}"
SCRIPT_DIR="$(dirname "$SOURCE")"
LOCAL_INSTALL_SCRIPT_PATH="${INSTALL_SCRIPT_PATH:-${SCRIPT_DIR}/../../installation}"
LOCAL_INSTALL_SCRIPT_PATH="${LOCAL_INSTALL_SCRIPT_PATH%/}"

export ENABLE_WEBAPP_PROD_DOWNLOAD=false
# Run installation (in interactive mode)
# y - start setup
# n - use static ip
# n - deactivate ipv6
# n - setup autohotspot
# - -   change default configuration (only with autohotspot = y)
# n - deactivate bluetooth
# n - disable on-chip audio
# - - mpd overwrite config (only with existing installation)
# n - setup rfid reader
# n - setup samba
# y - setup webapp
# y - build webapp
# y - setup kiosk mode
# n - reboot

"${LOCAL_INSTALL_SCRIPT_PATH}/install-jukebox.sh" <<< 'y
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
