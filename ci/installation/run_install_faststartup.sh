#!/usr/bin/env bash

# Install Phoniebox and test it
# Used e.g. for tests on Docker

# Objective:
# Test for disabling features (suggestions for faststartup). Skips installing all additionals.

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
# n - setup webapp
# - - install node (only with webapp = y)
# - - build webapp (only with install node = y)
# - - setup kiosk mode (only with webapp = y)
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
