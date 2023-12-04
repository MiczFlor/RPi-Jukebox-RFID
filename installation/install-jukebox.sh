#!/usr/bin/env bash
# One-line install script for the Jukebox Version 3
#
# To install, simply execute
# cd; bash <(wget -qO- https://raw.githubusercontent.com/MiczFlor/RPi-Jukebox-RFID/future3/develop/installation/install-jukebox.sh)
#
# If you want to get a specific branch or a different repository (mainly for developers)
# you may specify them like this
# cd; GIT_USER='MiczFlor' GIT_BRANCH='future3/develop' bash <(wget -qO- https://raw.githubusercontent.com/MiczFlor/RPi-Jukebox-RFID/future3/develop/installation/install-jukebox.sh)
#
export LC_ALL=C

# Set Repo variables if not specified when calling the script
GIT_USER=${GIT_USER:-"MiczFlor"}
GIT_BRANCH=${GIT_BRANCH:-"future3/main"}

# Constants
GIT_REPO_NAME="RPi-Jukebox-RFID"
GIT_URL="https://github.com/${GIT_USER}/${GIT_REPO_NAME}"
echo GIT_BRANCH $GIT_BRANCH
echo GIT_URL $GIT_URL

CURRENT_USER="${SUDO_USER:-$(whoami)}"
CURRENT_USER_GROUP=$(id -gn "$CURRENT_USER")
HOME_PATH=$(getent passwd "$CURRENT_USER" | cut -d: -f6)
echo "Current User: $CURRENT_USER"
echo "User home dir: $HOME_PATH"

INSTALLATION_PATH="${HOME_PATH}/${GIT_REPO_NAME}"
INSTALL_ID=$(date +%s)
INSTALLATION_LOGFILE="${HOME_PATH}/INSTALL-${INSTALL_ID}.log"

# Check if current distro is a 32 bit version
# Support for 64 bit Distros has not been checked (or precisely: is known not to work)
# All RaspianOS versions report as machine "armv6l" or "armv7l", if 32 bit (even the ARMv8 cores!)
_check_os_type() {
  local os_type=$(uname -m)

  echo -e "\nChecking OS type '$os_type'"

  if [[ $os_type == "armv7l" || $os_type == "armv6l" ]]; then
    echo -e "  ... OK!\n"
  else
    echo "ERROR: Only 32 bit operating systems supported. Please use a 32bit version of RaspianOS!"
    echo "You can fix this problem for 64bit kernels: https://github.com/MiczFlor/RPi-Jukebox-RFID/issues/2041"
    exit 1
  fi
}

# Manipulate file descriptor for logging
# Behavior:
# Write To logfile:
#   default stdout will only write to logfile
#   default stderr will only write to logfile
#       e.g echo "write only to logfile"
# Write To console (user window):
#   redirect to fd 3 will only write to the console
#       e.g. echo "write only to console" 1>&3
# Write To both:
#   use tee to write output to logfile and console
#       e.g. echo "write to both" | tee /dev/fd/3
_setup_logging(){
    if [ "$CI_RUNNING" == "true" ]; then
        exec 3>&1 2>&1
    else
        exec 3>&1 1>>"${INSTALLATION_LOGFILE}" 2>&1 || { echo "ERROR: Cannot create log file."; exit 1; }
    fi
    echo "Log start: ${INSTALL_ID}"
}

# Generic emergency error handler that exits the script immediately
# Print additional custom message if passed as first argument
# Examples:
#   a command || exit_on_error
#   a command || exit_on_error "Execution of command failed"
exit_on_error () {
  echo -e "\n****************************************" | tee /dev/fd/3
  echo "ERROR OCCURRED!
A non-recoverable error occurred.
Check install log for details:" | tee /dev/fd/3
  echo "$INSTALLATION_LOGFILE" | tee /dev/fd/3
  echo "****************************************" | tee /dev/fd/3
  if [[ -n $1 ]]; then
    echo "$1" | tee /dev/fd/3
    echo "****************************************" | tee /dev/fd/3
  fi
  echo "Abort!"
  exit 1
}

_download_jukebox_source() {
  echo -e "\n\n"
  echo "#########################################################"
  echo "Downloading Phoniebox software from Github ..." 1>&3
  echo "Download Source: ${GIT_URL}/${GIT_BRANCH}" | tee /dev/fd/3

  cd "${HOME_PATH}" || exit_on_error "ERROR: Changing to home dir failed."
  wget -qO- "${GIT_URL}/tarball/${GIT_BRANCH}" | tar xz
  # Use case insensitive search/sed because user names in Git Hub are case insensitive
  local git_repo_download=$(find . -maxdepth 1 -type d -iname "${GIT_USER}-${GIT_REPO_NAME}-*")
  echo "GIT REPO DOWNLOAD = $git_repo_download"
  GIT_HASH=$(echo "$git_repo_download" | sed -rn "s/.*${GIT_USER}-${GIT_REPO_NAME}-([0-9a-fA-F]+)/\1/ip")
  # Save the git hash for this particular download for later git repo initialization
  echo "GIT HASH = $GIT_HASH"
  if [[ -z "${git_repo_download}" ]]; then
    exit_on_error "ERROR: Couldn't find git download."
  fi
  if [[ -z "${GIT_HASH}" ]]; then
    exit_on_error "ERROR: Couldn't determine git hash from download."
  fi
  mv "$git_repo_download" "$GIT_REPO_NAME"
  echo -e "\nDONE: Downloading Phoniebox software from Github"
  echo "#########################################################"
}

_load_sources() {
    # Load / Source dependencies
    for i in "${INSTALLATION_PATH}"/installation/includes/*; do
    source "$i"
    done

    for j in "${INSTALLATION_PATH}"/installation/routines/*; do
    source "$j"
    done
}


### CHECK PREREQUISITE
_check_os_type

### SETUP LOGGING
_setup_logging

### RUN INSTALLATION
_download_jukebox_source
cd "${INSTALLATION_PATH}" || exit_on_error "ERROR: Changing to install dir failed."
_load_sources

welcome
run_with_timer install
finish
