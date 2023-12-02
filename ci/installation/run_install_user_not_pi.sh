#!/usr/bin/env bash

# Install Phoniebox and test it
# Used e.g. for tests on Docker

# Objective: Test installation with script using a simple configuration

SOURCE="${BASH_SOURCE[0]}"
SCRIPT_DIR="$(dirname "$SOURCE")"
LOCAL_INSTALL_SCRIPT_PATH="${INSTALL_SCRIPT_PATH:-${SCRIPT_DIR}/../../installation}"
LOCAL_INSTALL_SCRIPT_PATH="${LOCAL_INSTALL_SCRIPT_PATH%/}"

# Run installation (in interactive mode)
# - - Installation must abort early

"${LOCAL_INSTALL_SCRIPT_PATH}/install-jukebox.sh"
INSTALLATION_EXITCODE=$?

# only count abortion due to "not user pi" as success
if [ "${INSTALLATION_EXITCODE}" -eq 2 ]; then
    INSTALLATION_EXITCODE=0
else
    INSTALLATION_EXITCODE=1
fi
exit "${INSTALLATION_EXITCODE}"
