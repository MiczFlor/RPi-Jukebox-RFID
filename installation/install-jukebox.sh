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

# currently the user 'pi' is mandatory
# https://github.com/MiczFlor/RPi-Jukebox-RFID/issues/1785
_check_user() {
  if [ "${CURRENT_USER}" != "pi" ]; then
    echo
    echo "ERROR: User must be 'pi'!"
    echo "       Other usernames are currently not supported."
    echo "       Please check the wiki for further information"
    exit 2
  fi

  if [ "${HOME_PATH}" != "/home/pi" ]; then
    echo
    echo "ERROR: HomeDir must be '/home/pi'!"
    echo "       Other usernames are currently not supported."
    echo "       Please check the wiki for further information"
    exit 2
  fi

  if [ ! -d "${HOME_PATH}" ]; then
    echo
    echo "Warning: HomeDir ${HOME_PATH} does not exist."
    echo "         Please create it and start again."
    exit 2
  fi
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

download_jukebox_source() {
  wget -qO- "${GIT_URL}/tarball/${GIT_BRANCH}" | tar xz
  # Use case insensitive search/sed because user names in Git Hub are case insensitive
  GIT_REPO_DOWNLOAD=$(find . -maxdepth 1 -type d -iname "${GIT_USER}-${GIT_REPO_NAME}-*")
  echo "GIT REPO DOWNLOAD = $GIT_REPO_DOWNLOAD"
  GIT_HASH=$(echo "$GIT_REPO_DOWNLOAD" | sed -rn "s/.*${GIT_USER}-${GIT_REPO_NAME}-([0-9a-fA-F]+)/\1/ip")
  # Save the git hash for this particular download for later git repo initialization
  echo "GIT HASH = $GIT_HASH"
  if [[ -z "${GIT_REPO_DOWNLOAD}" ]]; then
    exit_on_error "ERROR: Couldn't find git download."
  fi
  if [[ -z "${GIT_HASH}" ]]; then
    exit_on_error "ERROR: Couldn't determine git hash from download."
  fi
  mv "$GIT_REPO_DOWNLOAD" "$GIT_REPO_NAME"
  unset GIT_REPO_DOWNLOAD
}


### CHECK PREREQUISITE
_check_os_type
_check_user

### RUN INSTALLATION
cd "${HOME_PATH}"
INSTALLATION_LOGFILE="${HOME_PATH}/INSTALL-${INSTALL_ID}.log"
if [ "$CI_RUNNING" == "true" ]; then
    exec 3>&1 2>&1
else
    exec 3>&1 1>>"${INSTALLATION_LOGFILE}" 2>&1 || { echo "Cannot create log file. Panic."; exit 1; }
fi
echo "Log start: ${INSTALL_ID}"

clear 1>&3
echo "Downloading Phoniebox software from Github ..." 1>&3
echo "Download Source: ${GIT_URL}/${GIT_BRANCH}" | tee /dev/fd/3

download_jukebox_source

cd "${INSTALLATION_PATH}" || exit_on_error "ERROR: Changing to install dir failed."
# Load / Source dependencies
for i in "${INSTALLATION_PATH}"/installation/includes/*; do
  source "$i"
done

for j in "${INSTALLATION_PATH}"/installation/routines/*; do
  source "$j"
done

welcome
run_with_timer install
finish
