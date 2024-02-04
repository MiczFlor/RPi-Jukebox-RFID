#!/usr/bin/env bash

# Install Phoniebox and test it
# Used e.g. for tests on Docker

# Objective:
# Test for the libzmq local build (no precompiled download)

SOURCE="${BASH_SOURCE[0]}"
SCRIPT_DIR="$(dirname "$SOURCE")"
LOCAL_INSTALL_SCRIPT_PATH="${INSTALL_SCRIPT_PATH:-${SCRIPT_DIR}/../../installation}"
LOCAL_INSTALL_SCRIPT_PATH="${LOCAL_INSTALL_SCRIPT_PATH%/}"

export BUILD_LIBZMQ_WITH_DRAFTS_ON_DEVICE=true
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
# n - setup webapp
# - - build webapp (only with webapp = y)
# - - setup kiosk mode (only with webapp = y)
# n - reboot

"${LOCAL_INSTALL_SCRIPT_PATH}/install-jukebox.sh" <<< 'y
n
n
n
n
n
n
n
n
n
'
