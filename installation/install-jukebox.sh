#!/usr/bin/env bash

# Bash Script output rules
# Output to both console and logfile:     "$ command | tee /dev/fd/3"
# Output to console only                  "$ command 1>&3"
# Output to logfile only:                 "$ command"
# No output to both console and logfile:  "$ command > /dev/null"

# Handle language configuration
export LC_ALL=C

# Constants
INSTALL_ID=$(date +%s)

HOME_PATH="/home/pi"
INSTALLATION_PATH="${HOME_PATH}/RPi-Jukebox-RFID"
SHARED_PATH="${INSTALLATION_PATH}/shared"
SETTINGS_PATH="${SHARED_PATH}/settings"

GIT_URL="https://github.com/MiczFlor/RPi-Jukebox-RFID.git"
GIT_BRANCH="future3/develop"

# Settings
ENABLE_STATIC_IP=true
DISABLE_BOOT_SCREEN=true
DISABLE_BOOT_LOGS_PRINT=true
ENABLE_KIOSK_MODE=false       # Allow web application to be shown via a display attached to RPi

# $1->start, $2->end
calc_runtime_and_print () {
  runtime=$(($2-$1))
  ((h=${runtime}/3600))
  ((m=(${runtime}%3600)/60))
  ((s=${runtime}%60))

  echo "Done in ${h}h ${m}m ${s}s."
}

### Method definitions
# Welcome Screen
welcome() {
  clear 1>&3
  echo "#########################################################
#                                                       #
#      ___  __ ______  _  __________ ____   __  _  _    #
#     / _ \/ // / __ \/ |/ /  _/ __/(  _ \ /  \( \/ )   #
#    / ___/ _  / /_/ /    // // _/   ) _ ((  O ))  (    #
#   /_/  /_//_/\____/_/|_/___/____/ (____/ \__/(_/\_)   #
#   future3                                             #
#                                                       #
#########################################################

You are turning your Raspberry Pi into a Phoniebox.
Good choice!

Depending on your hardware, this installation might last
around 60 minutes. It updates OS packages, installs
Phoniebox dependencies and registers settings. Be patient
and don't let your computer go to sleep. It might
disconnect your SSH connection causing the interuption of
the installation process.

Let's set up your Phoniebox now?! [Y/n]" 1>&3

  read -rp "Do you want to install? [Y/n] " response
  case "$response" in
    [nN][oO]|[nN])
      exit
      ;;
    *)
      echo "Starting installation ..." 1>&3
      ;;
  esac
}

# Update RPi configuration
set_raspi_config() {
  echo "Set default raspi-config" | tee /dev/fd/3
  # Source: https://raspberrypi.stackexchange.com/a/66939

  # Autologin
  echo "  * Enable Autologin for 'pi' user" 1>&3
  sudo raspi-config nonint do_boot_behaviour B2

  # Wait for network at boot
  # echo "  * Enable 'Wait for network at boot'" 1>&3
  # sudo raspi-config nonint do_boot_wait 1

  # power management of wifi: switch off to avoid disconnecting
  echo "  * Disable Wifi power management to avoid disconnecting" 1>&3
  sudo iwconfig wlan0 power off
}

# Update System
update_os() {
  local time_start=$(date +%s)

  echo "Updating Raspberry Pi OS" | tee /dev/fd/3
  sudo apt-get -qq -y update; sudo apt-get -qq -y full-upgrade; sudo apt-get -qq -y autoremove

  calc_runtime_and_print time_start $(date +%s)
  echo "DONE: update_os"
}

# Install Dependencies
install_jukebox_dependencies() {
  local time_start=$(date +%s)

  # Skip interactive Samba WINS config dialog
  echo "samba-common samba-common/dhcp boolean false" | sudo debconf-set-selections

  echo "Install Jukebox OS dependencies" | tee /dev/fd/3
  sudo apt-get -qq -y update; sudo apt-get -qq -y install \
    at git wget \
    mpd mpc \
    mpg123 \
    samba samba-common-bin \
    python3 python3-dev python3-pip python3-setuptools python3-mutagen python3-gpiozero \
    ffmpeg \
    alsa-tools \
    --no-install-recommends \
    --allow-downgrades \
    --allow-remove-essential \
    --allow-change-held-packages

  # Install Python
  sudo update-alternatives --install /usr/bin/python python /usr/bin/python3.7 1

  # Install Node
  if which node > /dev/null; then
    echo "  Found existing NodeJS. Hence, updating NodeJS"
    sudo npm cache clean -f
    sudo npm install --silent -g n
    sudo n --quiet latest
    sudo npm update --silent -g
  else
    echo "  Install NodeJS"
    curl -sL https://deb.nodesource.com/setup_16.x | sudo -E bash -
    sudo apt-get -qq -y install nodejs
    sudo npm install --silent -g npm serve

    # Slower PIs need this to finish building the Webapp
    MEMORY=`cat /proc/meminfo | awk '$1 == "MemTotal:" {print 0+$2}'`
    if [[ $MEMORY -lt 1024000 ]]
    then
      export NODE_OPTIONS=--max-old-space-size=1024
    fi

    if [[ $MEMORY -lt 512000 ]]
    then
      export NODE_OPTIONS=--max-old-space-size=512
    fi
  fi

  calc_runtime_and_print time_start $(date +%s)
  echo "DONE: install_jukebox_dependencies"
}

# Install Jukebox
install_jukebox() {
  local time_start=$(date +%s)

  echo "Install Jukebox" | tee /dev/fd/3
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
      git pull
    fi
  else
    git clone --depth 1 ${GIT_URL} --branch "${GIT_BRANCH}"
  fi

  # Install Python dependencies
  echo "  Install Python dependencies" | tee /dev/fd/3
  # ZMQ
  # Because the latest stable release of ZMQ does not support WebSockets
  # we need to compile the latest version in Github
  # As soon WebSockets support is stable in ZMQ, this can be removed
  # Sources:
  # https://pyzmq.readthedocs.io/en/latest/draft.html
  # https://github.com/MonsieurV/ZeroMQ-RPi/blob/master/README.md
  echo "    Install pyzmq"
  ZMQ_TMP_PATH="libzmq"
  ZMQ_PREFIX="/usr/local"

  if ! pip3 list | grep -F pyzmq >> /dev/null; then
    cd ${HOME_PATH} && mkdir ${ZMQ_TMP_PATH} && cd ${ZMQ_TMP_PATH}
    # Download pre-compiled libzmq armv6 from Google Drive
    # https://drive.google.com/file/d/1KP6BqLF-i2dCUsHhOUpOwwuOmKsB5GKY/view?usp=sharing
    wget --quiet --load-cookies /tmp/cookies.txt "https://docs.google.com/uc?export=download&confirm=$(wget --quiet --save-cookies /tmp/cookies.txt --keep-session-cookies --no-check-certificate 'https://docs.google.com/uc?export=download&id=1KP6BqLF-i2dCUsHhOUpOwwuOmKsB5GKY' -O- | sed -rn 's/.*confirm=([0-9A-Za-z_]+).*/\1\n/p')&id=1KP6BqLF-i2dCUsHhOUpOwwuOmKsB5GKY" -O libzmq.tar.gz && rm -rf /tmp/cookies.txt
    tar -xzf libzmq.tar.gz
    rm -f libzmq.tar.gz
    sudo rsync -a * ${ZMQ_PREFIX}/

    pip3 install --pre pyzmq \
      --install-option=--enable-drafts \
      --install-option=--zmq=${ZMQ_PREFIX}
  else
    echo "      Skipping. pyzmq already installed"
  fi

  echo "    Install requirements"
  cd ${INSTALLATION_PATH}
  pip3 install --no-cache-dir -r ${INSTALLATION_PATH}/requirements.txt

  # Install Node dependencies
  # TODO: Avoid building the app locally
  # Instead implement a Github Action that prebuilds on commititung a git tag
  echo "  Install web application" | tee /dev/fd/3
  cd ${INSTALLATION_PATH}/src/webapp
  npm ci --prefer-offline --no-audit --production
  rm -rf build
  npm run build

  calc_runtime_and_print time_start $(date +%s)
  echo "DONE: install_jukebox"
}

# Samba configuration settings
setup_samba() {
  local SMB_CONF="/etc/samba/smb.conf"
  local SMB_USER="pi"
  local SMB_PASSWD="raspberry"

  echo "Configure Samba" | tee /dev/fd/3
  # Samba has not been configured
  if grep -q "## Jukebox Samba Config" "$SMB_CONF"; then
    echo "  Skipping. Already set up!" | tee /dev/fd/3
  else
    # Create Samba user
    (echo "${SMB_PASSWD}"; echo "${SMB_PASSWD}") | sudo smbpasswd -s -a $SMB_USER

    sudo chown root:root $SMB_CONF
    sudo chmod 777 $SMB_CONF

    # Create Samba Mount Points
    sudo cat << EOF >> $SMB_CONF
## Jukebox Samba Config
[phoniebox]
  comment= Pi Jukebox
  path=${SHARED_PATH}
  browseable=Yes
  writeable=Yes
  only guest=no
  create mask=0777
  directory mask=0777
  public=no
EOF

    sudo chmod 644 $SMB_CONF
  fi

  echo "DONE: setup_samba"
}

register_jukebox_settings() {
  echo "Register Jukebox settings" | tee /dev/fd/3

  # TODO
  # Ask for Jukebox Name
  # Ask for Jukebox hostname to replace raspberry.local

  cp -f ${INSTALLATION_PATH}/resources/default-settings/jukebox.default.yaml ${SETTINGS_PATH}/jukebox.yaml
  cp -f ${INSTALLATION_PATH}/resources/default-settings/logger.default.yaml ${SETTINGS_PATH}/logger.yaml

  echo "DONE: register_jukebox_settings"
}

register_system_services() {
  local time_start=$(date +%s)
  local SYSTEMD_PATH="/lib/systemd/system"

  echo "Register system services" | tee /dev/fd/3
  sudo cp -f ${INSTALLATION_PATH}/resources/default-services/jukebox-*.service ${SYSTEMD_PATH}
  sudo chmod 644 ${SYSTEMD_PATH}/jukebox-*.service

  sudo systemctl enable jukebox-daemon.service
  sudo systemctl enable jukebox-webapp.service

  sudo systemctl daemon-reload

  echo "Configure MPD" | tee /dev/fd/3
  # TODO: Could this be read from the jukebox.yaml?
  local MPD_CONF_PATH="${SETTINGS_PATH}/mpd.conf"
  local AUDIOFOLDERS_PATH="${SHARED_PATH}/audiofolders"
  local PLAYLISTS_PATH="${SHARED_PATH}/playlists"
  local ALSA_MIXER_CONTROL="Headphone"

  sudo systemctl stop mpd.service

  # Prepare new mpd.conf
  sudo cp -f ${INSTALLATION_PATH}/resources/default-settings/mpd.default.conf ${MPD_CONF_PATH}
  sudo sed -i 's|%%JUKEBOX_AUDIOFOLDERS_PATH%%|'"$AUDIOFOLDERS_PATH"'|' ${MPD_CONF_PATH}
  sudo sed -i 's|%%JUKEBOX_PLAYLISTS_PATH%%|'"$PLAYLISTS_PATH"'|' ${MPD_CONF_PATH}
  sudo sed -i 's|%%JUKEBOX_ALSA_MIXER_CONTROL%%|'"$ALSA_MIXER_CONTROL"'|' ${MPD_CONF_PATH}

  # Reload mpd
  # Make original file unreachable
  sudo mv -f /etc/mpd.conf /etc/mpd.conf.orig
  # Update mpd.service file to use Jukebox mpd.conf
  sudo sed -i 's|$MPDCONF|'"$MPD_CONF_PATH"'|' ${SYSTEMD_PATH}/mpd.service
  sudo systemctl daemon-reload
  sudo systemctl start mpd.service
  mpc update

  # We don't start the services now, we wait for the reboot
  calc_runtime_and_print time_start $(date +%s)
  echo "DONE: register_system_services"
}

install_rfid_reader() {
  local time_start=$(date +%s)

  python3 ${INSTALLATION_PATH}/src/jukebox/run_register_rfid_reader.py | tee /dev/fd/3

  calc_runtime_and_print time_start $(date +%s)
  echo "DONE: install_rfid_reader"
}

install_kiosk_mode() {
  local time_start=$(date +%s)

  if [ "$ENABLE_KIOSK_MODE" = true ] ; then
    local time_start=$(date +%s)
    echo "Setup Kiosk Mode" | tee /dev/fd/3

    # Resource:
    # https://blog.r0b.io/post/minimal-rpi-kiosk/
    sudo apt-get -qq -y install --no-install-recommends \
      xserver-xorg \
      x11-xserver-utils \
      xinit \
      openbox \
      chromium-browser

    local _DISPLAY='$DISPLAY'
    local _XDG_VTNR='$XDG_VTNR'
    cat << EOF >> /home/pi/.bashrc

## Jukebox kiosk autostart
[[ -z $_DISPLAY && $_XDG_VTNR -eq 1 ]] && startx -- -nocursor

EOF

    local XINITRC='/etc/xdg/openbox/autostart'
    cat << EOF | sudo tee -a $XINITRC

## Jukebox Kiosk Mode
# Disable any form of screen saver / screen blanking / power management
xset s off
xset s noblank
xset -dpms

# Start Chromium in kiosk mode
sed -i 's/"exited_cleanly":false/"exited_cleanly":true/' ~/.config/chromium/'Local State'
sed -i 's/"exited_cleanly":false/"exited_cleanly":true/; s/"exit_type":"[^"]\+"/"exit_type":"Normal"/' ~/.config/chromium/Default/Preferences
chromium-browser http://localhost \
  --disable-infobars \
  --disable-pinch \
  --disable-translate \
  --kiosk \
  --noerrdialogs \
  --no-first-run

EOF

    # Resource: https://github.com/Thyraz/Sonos-Kids-Controller/blob/d1f061f4662c54ae9b8dc8b545f9c3ba39f670eb/README.md#kiosk-mode-installation
    sudo touch /etc/chromium-browser/customizations/01-disable-update-check;echo CHROMIUM_FLAGS=\"\$\{CHROMIUM_FLAGS\} --check-for-update-interval=31536000\" | sudo tee /etc/chromium-browser/customizations/01-disable-update-check

  else
    echo "Kiosk mode not enabled. Skipping installation."
  fi

  calc_runtime_and_print time_start $(date +%s)
  echo "DONE: setup_kiosk_mode"
}

# Reduce the amount of time for the Raspberry to boot
optimize_boot_time() {
  local time_start=$(date +%s)

  # Reference: https://panther.software/configuration-code/raspberry-pi-3-4-faster-boot-time-in-few-easy-steps/
  echo "Optimize boot time" | tee /dev/fd/3

  echo "  * Disable hciuart.service" | tee /dev/fd/3
  sudo systemctl disable hciuart.service

  echo "  * Disable keyboard-setup.service" | tee /dev/fd/3
  sudo systemctl disable keyboard-setup.service

  echo "  * Disable triggerhappy.service" | tee /dev/fd/3
  sudo systemctl disable triggerhappy.service

  echo "  * Disable raspi-config.service" | tee /dev/fd/3
  sudo systemctl disable raspi-config.service

  echo "  * Disable apt-daily.service & apt-daily-upgrade.service" | tee /dev/fd/3
  sudo systemctl disable apt-daily.service
  sudo systemctl disable apt-daily-upgrade.service

  # Static IP Address and DHCP optimizations
  local DHCP_CONF="/etc/dhcpcd.conf"

  if [ "$ENABLE_STATIC_IP" = true ] ; then
    echo "  * Set static IP address and disabling IPV6" | tee /dev/fd/3
    if grep -q "## Jukebox DHCP Config" "$DHCP_CONF"; then
      echo "    Skipping. Already set up!" | tee /dev/fd/3
    else
      # DHCP has not been configured
      # Reference: https://unix.stackexchange.com/a/307790/478030
      INTERFACE=$(route | grep '^default' | grep -o '[^ ]*$')

      # Reference: https://serverfault.com/a/31179/431930
      GATEWAY=$(route -n | grep 'UG[ \t]' | awk '{print $2}')

      # Using the dynamically assigned IP address as it is the best guess to be free
      # Reference: https://unix.stackexchange.com/a/48254/478030
      CURRENT_IP_ADDRESS=$(hostname -I)
      echo "    * ${INTERFACE} is the default network interface" | tee /dev/fd/3
      echo "    * ${GATEWAY} is the Router Gateway address" | tee /dev/fd/3
      echo "    * Using ${CURRENT_IP_ADDRESS} as the static IP for now" | tee /dev/fd/3

      cat << EOF | sudo tee -a $DHCP_CONF

## Jukebox DHCP Config
interface ${INTERFACE}
static ip_address=${CURRENT_IP_ADDRESS}/24
static routers=${GATEWAY}
static domain_name_servers=${GATEWAY}

noarp
ipv4only
noipv6

EOF

    fi
  else
    echo "  * Skipped static IP address and disabling IPV6"
  fi

  # Disable RPi rainbow screen
  if [ "$DISABLE_BOOT_SCREEN" = true ] ; then
    echo "  * Disable RPi rainbow screen" | tee /dev/fd/3
    BOOT_CONFIG='/boot/config.txt'
    cat << EOF | sudo tee -a $BOOT_CONFIG

## Jukebox Settings
disable_splash=1

EOF
  fi

  # Disable boot logs
  if [ "$DISABLE_BOOT_LOGS_PRINT" = true ] ; then
    echo "  * Disable boot logs" | tee /dev/fd/3
    BOOT_CMDLINE='/boot/cmdline.txt'
    sudo sed -i "$ s/$/ consoleblank=1 logo.nologo quiet loglevel=0 plymouth.enable=0 vt.global_cursor_default=0 plymouth.ignore-serial-consoles splash fastboot noatime nodiratime noram/" $BOOT_CMDLINE
  fi


  calc_runtime_and_print time_start $(date +%s)
  echo "DONE: optimize_boot_time"
}

cleanup() {
  sudo rm -rf /var/lib/apt/lists/*

  echo "DONE: cleanup"
}

finish() {
  echo "
---

Installation complete!

In order to start, you need to reboot your Raspberry Pi.
Your SSH connection will disconnect.

After the reboot, open either http://raspberrypi.local
(for Mac / iOS) or http://raspberrypi (for Android / Windows)
in a browser to get started. Don't forget to upload files
via Samba.

Do you want to reboot now? [Y/n]" 1>&3

  read -rp "Do you want to install? [Y/n] " response
  case "$response" in
    [nN][oO]|[nN])
      echo "Reboot aborted" | tee /dev/fd/3
      echo "DONE: finish"
      exit
      ;;
    *)
      echo "Rebooting ..." | tee /dev/fd/3
      echo "DONE: finish"
      sudo reboot
      ;;
  esac
}

install() {
  local time_start=$(date +%s)

  welcome
  set_raspi_config
  # update_os
  install_jukebox_dependencies
  setup_samba
  install_jukebox
  register_jukebox_settings
  register_system_services
  install_rfid_reader
  install_kiosk_mode
  optimize_boot_time
  cleanup

  calc_runtime_and_print time_start $(date +%s) | tee /dev/fd/3

  finish
}

### RUN INSTALLATION

# Log installation for debugging reasons
INSTALLATION_LOGFILE="${HOME_PATH}/INSTALL-${INSTALL_ID}.log"
# Source: https://stackoverflow.com/questions/18460186/writing-outputs-to-log-file-and-console
exec 3>&1 1>>${INSTALLATION_LOGFILE} 2>&1
echo "Log start: ${INSTALL_ID}"

install
