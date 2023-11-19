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
# - - Installation must abort early

"$local_install_script_path"/install-jukebox.sh
INSTALLATION_EXITCODE=$?

# only count abortion due to "not user pi" as success
if [ "${INSTALLATION_EXITCODE}" -eq 2 ]; then
    INSTALLATION_EXITCODE=0
else
    INSTALLATION_EXITCODE=1
fi
exit "${INSTALLATION_EXITCODE}"
