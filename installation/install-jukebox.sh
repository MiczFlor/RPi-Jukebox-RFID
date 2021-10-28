#!/usr/bin/env bash
export LC_ALL=C

# Variables
GIT_USER="MiczFlor"
GIT_BRANCH="future3/main"

# Constants
GIT_REPO_NAME="RPi-Jukebox-RFID"
GIT_URL="https://github.com/${GIT_USER}/${GIT_REPO_NAME}"
HOME_PATH="/home/pi"
INSTALLATION_PATH="${HOME_PATH}/${GIT_REPO_NAME}"
SHARED_PATH="${INSTALLATION_PATH}/shared"
SETTINGS_PATH="${SHARED_PATH}/settings"
SYSTEMD_PATH="/lib/systemd/system"
INSTALL_ID=$(date +%s)

download_jukebox_source() {
  wget -qO- ${GIT_URL}/tarball/${GIT_BRANCH} | tar xz
  find . -maxdepth 1 -type d -name "${GIT_USER}-${GIT_REPO_NAME}-*" -exec mv {} $GIT_REPO_NAME  \;
}

### RUN INSTALLATION
INSTALLATION_LOGFILE="${HOME_PATH}/INSTALL-${INSTALL_ID}.log"
exec 3>&1 1>>${INSTALLATION_LOGFILE} 2>&1
echo "Log start: ${INSTALL_ID}"

clear 1>&3
echo "Downloading Phoniebox software from Github ..." 1>&3
echo "Download Source: ${GIT_URL}/${GIT_BRANCH}" | tee /dev/fd/3

download_jukebox_source
cd ${INSTALLATION_PATH}

# Load / Source dependencies
for i in $INSTALLATION_PATH/installation/includes/*;
  do source $i
done

for j in $INSTALLATION_PATH/installation/routines/*;
  do source $j
done

welcome
run_with_timer install
finish
