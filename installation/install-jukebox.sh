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
GIT_BRANCH="future3/main"

# Settings
ENABLE_STATIC_IP=true
DISABLE_IPv6=true
DISABLE_BLUETOOTH=true
DISABLE_SSH_QOS=true
DISABLE_BOOT_SCREEN=true
DISABLE_BOOT_LOGS_PRINT=true
MPD_USE_DEFAULT_CONF_DIR=true
MPD_CONFIG=true
UPDATE_OS=false
INSTALL_WEBAPP=true
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

customize_options() {
  echo "Customize Options begins"
  echo "A few more questions before we can start ..." 1>&3

  # future3/main (release branch) or future3/develop (current branch)
  read -n 1 -p "Would you like to install 1) latest release candidate or 2) most recent development? [R/d] " ans;
  case $ans in
      # r|R) Ignoring R actually as it is the default
      #  GIT_BRANCH="future3/main"
      s|d)
        GIT_BRANCH="future3/develop"
        ;;
      *)
        ;;
  esac
  echo "Installing ${GIT_BRANCH}" | tee /dev/fd/3

  # ENABLE_STATIC_IP
  CURRENT_IP_ADDRESS=$(hostname -I)
  read -rp "Would you like to set a static IP (will be ${CURRENT_IP_ADDRESS})?
It'll save a lot of start up time. This can be changed later.
[Y/n] " response
  case "$response" in
    [nN][oO]|[nN])
      ENABLE_STATIC_IP=false
      ;;
    *)
      ;;
  esac
  echo "ENABLE_STATIC_IP=${ENABLE_STATIC_IP}"

  # DISABLE_IPv6
  read -rp "Do you want to disable IPv6? [Y/n] " response
  case "$response" in
    [nN][oO]|[nN])
      DISABLE_IPv6=false
      ;;
    *)
      ;;
  esac
  echo "DISABLE_IPv6=${DISABLE_IPv6}"

  # DISABLE_BLUETOOTH
  read -rp "Do you want to disable Bluethooth?
We recommend to turn off Bluetooth to save energy and booting time.
[Y/n] " response
  case "$response" in
    [nN][oO]|[nN])
      DISABLE_BLUETOOTH=false
      ;;
    *)
      ;;
  esac
  echo "DISABLE_BLUETOOTH=${DISABLE_BLUETOOTH}"

  # DISABLE_BOOT_SCREEN
  read -rp "Do you want to disable the Rainbow boot screen?
We recommend to turn off it off booting time.
[Y/n] " response
  case "$response" in
    [nN][oO]|[nN])
      DISABLE_BOOT_SCREEN=false
      ;;
    *)
      ;;
  esac
  echo "DISABLE_BOOT_SCREEN=${DISABLE_BOOT_SCREEN}"

  # DISABLE_BOOT_LOGS_PRINT
  read -rp "Do you want to disable the boot logs?
We recommend to turn off it off booting time. You will have to
enable it if you need to debug the booting routine for some reason.
[Y/n] " response
  case "$response" in
    [nN][oO]|[nN])
      DISABLE_BOOT_LOGS_PRINT=false
      ;;
    *)
      ;;
  esac
  echo "DISABLE_BOOT_LOGS_PRINT=${DISABLE_BOOT_LOGS_PRINT}"

  # INSTALL_WEBAPP
  read -rp "Would you like to install the web application?
If you don't want to use a graphical interface to manage your Phoniebox,
you don't need to install the web application.
[y/N] " response
  case "$response" in
    [nN][oO]|[nN])
      INSTALL_WEBAPP=false
      ENABLE_KIOSK_MODE=false
      ;;
    *)
      ;;
  esac
  echo "INSTALL_WEBAPP=${INSTALL_WEBAPP}"

  # ENABLE_KIOSK_MODE
  if [ "$INSTALL_WEBAPP" = true ] ; then
    read -rp "Would you like to enable the Kiosk Mode?
  If you have a screen attached to your RPi, this will launch the
  web application right after boot. It will only install the necessary
  xserver dependencies and not the entire RPi desktop environment.
  [y/N] " response
    case "$response" in
      [yY])
        ENABLE_KIOSK_MODE=true
        ;;
      *)
        ;;
    esac
    echo "ENABLE_KIOSK_MODE=${ENABLE_KIOSK_MODE}"
  fi

  # UPDATE_OS
  read -rp "Would you like to update the operating system?
This shall be done eventually, but increases the installation time a lot.
[y/N] " response
  case "$response" in
    [yY])
      UPDATE_OS=true
      ;;
    *)
      ;;
  esac
  echo "UPDATE_OS=${UPDATE_OS}"

  echo "Customize Options ends"
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

  if [ "$UPDATE_OS" = true ] ; then
    echo "Updating Raspberry Pi OS" | tee /dev/fd/3
    sudo apt-get -qq -y update; sudo apt-get -qq -y full-upgrade; sudo apt-get -qq -y autoremove
  else
    echo "Raspberry Pi OS Update skipped"
  fi

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

  if [ "$INSTALL_WEBAPP" = true ] ; then
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

  if [ "$INSTALL_WEBAPP" = true ] ; then
    # Install Node dependencies
    # TODO: Avoid building the app locally
    # Instead implement a Github Action that prebuilds on commititung a git tag
    echo "  Install web application" | tee /dev/fd/3
    cd ${INSTALLATION_PATH}/src/webapp
    npm ci --prefer-offline --no-audit --production
    rm -rf build
    npm run build
  fi

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

  if [ "$MPD_CONFIG" = true ] ; then

    echo "Configure MPD" | tee /dev/fd/3
    # TODO: Could this be read from the jukebox.yaml?

    local AUDIOFOLDERS_PATH="${SHARED_PATH}/audiofolders"
    local PLAYLISTS_PATH="${SHARED_PATH}/playlists"
    local ALSA_MIXER_CONTROL="Headphone"

    sudo systemctl stop mpd.service

    local MPD_CONF_PATH="/etc/mpd.conf"
    if [ "$MPD_USE_DEFAULT_CONF_DIR" = true ] ; then
      # As an option, the mpd.conf can be located in the Jukebox installation path
      # TODO: If so done, also update the jukebox.yaml to point to the correct location!
      local MPD_CONF_PATH="${SETTINGS_PATH}/mpd.conf"
        # Update mpd.service file to use Jukebox mpd.conf
        sudo sed -i 's|$MPDCONF|'"$MPD_CONF_PATH"'|' ${SYSTEMD_PATH}/mpd.service
    fi

    # Make a backup of original file (and make it unreachable in case of non-default conf location)
    sudo mv -f /etc/mpd.conf /etc/mpd.conf.orig

    # Prepare new mpd.conf
    sudo cp -f ${INSTALLATION_PATH}/resources/default-settings/mpd.default.conf ${MPD_CONF_PATH}
    sudo sed -i 's|%%JUKEBOX_AUDIOFOLDERS_PATH%%|'"$AUDIOFOLDERS_PATH"'|' ${MPD_CONF_PATH}
    sudo sed -i 's|%%JUKEBOX_PLAYLISTS_PATH%%|'"$PLAYLISTS_PATH"'|' ${MPD_CONF_PATH}
    sudo sed -i 's|%%JUKEBOX_ALSA_MIXER_CONTROL%%|'"$ALSA_MIXER_CONTROL"'|' ${MPD_CONF_PATH}
    sudo chown mpd:audio "${MPD_CONF_PATH}"
    sudo chmod 640 "${MPD_CONF_PATH}"

    # Reload mpd
    sudo systemctl daemon-reload
    sudo systemctl start mpd.service
    mpc update

  fi

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

  echo "  * Disable exim4.service" | tee /dev/fd/3
  sudo systemctl disable exim4.service

  if [ "$DISABLE_BLUETOOTH" = true ] ; then
    echo "  * Disable hciuart.service and bluetooth" | tee /dev/fd/3
    sudo systemctl disable hciuart.service
    sudo systemctl disable bluetooth.service
  fi

  echo "  * Disable keyboard-setup.service" | tee /dev/fd/3
  sudo systemctl disable keyboard-setup.service

  echo "  * Disable triggerhappy.service" | tee /dev/fd/3
  sudo systemctl disable triggerhappy.service
  sudo systemctl disable triggerhappy.socket

  echo "  * Disable raspi-config.service" | tee /dev/fd/3
  sudo systemctl disable raspi-config.service

  echo "  * Disable apt-daily.service & apt-daily-upgrade.service" | tee /dev/fd/3
  sudo systemctl disable apt-daily.service
  sudo systemctl disable apt-daily-upgrade.service
  sudo systemctl disable apt-daily.timer
  sudo systemctl disable apt-daily-upgrade.timer

  # Static IP Address and DHCP optimizations
  local DHCP_CONF="/etc/dhcpcd.conf"

  if [ "$ENABLE_STATIC_IP" = true ] ; then
    echo "  * Set static IP address" | tee /dev/fd/3
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

EOF

    fi
  else
    echo "  * Skipped static IP address"
  fi

  # Disable IPv6 and ARP
  if [ "$DISABLE_IPv6" = true ] ; then
      echo "  * Disabling IPV6 and ARP" | tee /dev/fd/3
      cat << EOF | sudo tee -a $DHCP_CONF

## Jukebox boot speed-up settings
noarp
ipv4only
noipv6

EOF

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

set_ssh_qos() {
  # The latest version of SSH installed on the Raspberry Pi 3 uses QoS headers, which disagrees with some
  # routers and other hardware. This causes immense delays when remotely accessing the RPi over ssh.
  if [ "$DISABLE_SSH_QOS" = true ] ; then
    echo "  * Set SSH QoS to best effort" | tee /dev/fd/3
    echo -e "IPQoS 0x00 0x00\n" | sudo tee -a /etc/ssh/sshd_config
    echo -e "IPQoS 0x00 0x00\n" | sudo tee -a /etc/ssh/ssh_config
  fi
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

  read -rp "Do you want to reboot now? [Y/n] " response
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
  update_os
  install_jukebox_dependencies
  setup_samba
  install_jukebox
  register_jukebox_settings
  register_system_services
  install_rfid_reader
  install_kiosk_mode
  optimize_boot_time
  set_ssh_qos
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
