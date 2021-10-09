#!/usr/bin/env bash

# Handle language configuration
export LC_ALL=C

# Constants
INSTALL_ID=$(date +%s)
GIT_URL="https://github.com/pabera/RPi-Jukebox-RFID.git"
GIT_BRANCH="future3/refactor-install-script"

HOME_PATH="/home/pi"
INSTALLATION_PATH="${HOME_PATH}/RPi-Jukebox-RFID"
SHARED_PATH="${INSTALLATION_PATH}/shared"
SETTINGS_PATH="${SHARED_PATH}/settings"
SYSTEMD_PATH="/lib/systemd/system"

clone_or_pull_jukebox_repository() {
  echo "Download Jukebox Repository" | tee /dev/fd/3
  cd ${HOME_PATH}

  if [ -d "$INSTALLATION_PATH" ]; then
    cd ${INSTALLATION_PATH}
    if [[ `git status --porcelain` ]]; then
      echo "  Found local changes in git repository. Moving them to backup branch 'local-backup-$INSTALL_ID' and git stash" | tee /dev/fd/3
      # Changes
      git fetch --all
      git checkout -b local-backup-$INSTALL_ID
      git stash
      git checkout $GIT_BRANCH
      git reset --hard origin/$GIT_BRANCH
    else
      # No changes
      echo "  Updating version"
      git pull origin $(git rev-parse --abbrev-ref HEAD)
    fi
  else
    git clone --depth 1 ${GIT_URL} --branch "${GIT_BRANCH}"
  fi

  echo "DONE: download_jukebox_repository"

  clear 1>&3
}

install() {
  customize_options
  set_raspi_config
  if [ "$DISABLE_SSH_QOS" = true ] ; then set_ssh_qos fi
  if [ "$UPDATE_RASPI_OS" = true ] ; then update_raspi_os fi
  setup_jukebox_core
  if [ "$MPD_CONFIG" = true ] ; then setup_mpd fi
  if [ "$INSTALL_SAMBA" = true ] ; then setup_samba fi
  setup_rfid_reader
  if [ "$INSTALL_WEBAPP" = true ] ; then setup_jukebox_webapp fi
  if [ "$ENABLE_KIOSK_MODE" = true ] ; then setup_kiosk_mode fi
  optimize_boot_time
  cleanup
}

### RUN INSTALLATION
# Log installation for debugging reasons
INSTALLATION_LOGFILE="${HOME_PATH}/INSTALL-${INSTALL_ID}.log"
# Source: https://stackoverflow.com/questions/18460186/writing-outputs-to-log-file-and-console
exec 3>&1 1>>${INSTALLATION_LOGFILE} 2>&1
echo "Log start: ${INSTALL_ID}"

clone_or_pull_jukebox_repository

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
