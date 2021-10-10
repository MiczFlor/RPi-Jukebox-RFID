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

download_jukebox_source() {
  wget -qO- https://github.com/pabera/RPi-Jukebox-RFID/tarball/future3/refactor-install-script | tar xz &&
  find . -maxdepth 1 -type d -name '*-RPi-Jukebox-RFID-*' -exec mv {} RPi-Jukebox-RFID  \;
}

install() {
  customize_options
  clear 1>&3
  set_raspi_config
  if [ "$DISABLE_SSH_QOS" = true ] ; then set_ssh_qos; fi;
  if [ "$UPDATE_RASPI_OS" = true ] ; then update_raspi_os; fi;
  setup_jukebox_core
  if [ "$MPD_CONFIG" = true ] ; then setup_mpd; fi;
  if [ "$ENABLE_SAMBA" = true ] ; then setup_samba; fi;
  setup_rfid_reader
  if [ "$ENABLE_WEBAPP" = true ] ; then setup_jukebox_webapp; fi;
  if [ "$ENABLE_KIOSK_MODE" = true ] ; then setup_kiosk_mode; fi;
  optimize_boot_time
  cleanup
}

### RUN INSTALLATION
# Log installation for debugging reasons
INSTALLATION_LOGFILE="${HOME_PATH}/INSTALL-${INSTALL_ID}.log"
# Source: https://stackoverflow.com/questions/18460186/writing-outputs-to-log-file-and-console
exec 3>&1 1>>${INSTALLATION_LOGFILE} 2>&1
echo "Log start: ${INSTALL_ID}"

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
