#!/usr/bin/env bash
# Handle language configuration
export LC_ALL=C

# Constants
INSTALL_ID=$(date +%s)

HOME_DIR="/home/pi"
INSTALLATION_DIR="${HOME_DIR}/RPi-Jukebox-RFID"
SHARED_DIR="${INSTALLATION_DIR}/shared"
SETTINGS_DIR="${SHARED_DIR}/settings"

GIT_URL="https://github.com/MiczFlor/RPi-Jukebox-RFID.git"
GIT_BRANCH="future3/webapp"

# $1->start, $2->end
calc_runtime_and_print () {
  runtime=$(($2-$1))
  ((h=${runtime}/3600))
  ((m=(${runtime}%3600)/60))
  ((s=${runtime}%60))

  echo "Done in ${h}h ${m}m ${s}s." | tee /dev/fd/3
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
  echo "  * Enable 'Wait for network at boot'" 1>&3
  sudo raspi-config nonint do_boot_wait 1
  # power management of wifi: switch off to avoid disconnecting
  echo "  * Disable Wifi power management to avoid disconnecting" 1>&3
  sudo iwconfig wlan0 power off
  # Switch off Bluetooth to save energy
  echo "  * Disable Bluetooth service to save energy" 1>&3
  sudo systemctl stop bluetooth
  # Skip interactive Samba WINS config dialog
  echo "samba-common samba-common/dhcp boolean false" | sudo debconf-set-selections
}

# Update System
update_os() {
  local time_start=$(date +%s)

  echo "Updating Raspberry Pi OS" | tee /dev/fd/3
  sudo apt-get -qq -y update; sudo apt-get -qq -y full-upgrade > /dev/null; sudo apt-get -qq -y autoremove > /dev/null

  calc_runtime_and_print time_start $(date +%s)
}

# Install Dependencies
install_jukebox_dependencies() {
  local time_start=$(date +%s)

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
    --allow-change-held-packages > /dev/null
  sudo rm -rf /var/lib/apt/lists/*

  # Install Python
  sudo update-alternatives --install /usr/bin/python python /usr/bin/python3.7 1

  # Install Node
  if which node > /dev/null; then
    echo "  Found existing NodeJS. Hence, updating NodeJS"
    sudo npm cache clean -f
    sudo n --quiet latest
    sudo npm update --silent -g
  else
    echo "  Install NodeJS"
    curl -sL https://deb.nodesource.com/setup_16.x | sudo -E bash - > /dev/null
    sudo apt-get -qq -y install nodejs
    sudo npm install --silent -g n npm serve
  fi

  calc_runtime_and_print time_start $(date +%s)
}

# Install Jukebox
install_jukebox() {
  local time_start=$(date +%s)

  echo "Install Jukebox" | tee /dev/fd/3
  cd ${HOME_DIR}

  if [ -d "$INSTALLATION_DIR" ]; then
    cd ${INSTALLATION_DIR}
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
  echo "  Install Python dependencies"
  # ZMQ
  # Because the latest stable release of ZMQ does not support WebSockets
  # we need to compile the latest version in Github
  # As soon WebSockets support is stable in ZMQ, this can be removed
  # Sources:
  # https://pyzmq.readthedocs.io/en/latest/draft.html
  # https://github.com/MonsieurV/ZeroMQ-RPi/blob/master/README.md
  echo "    Install pyzmq"
  ZMQ_TMP_DIR="libzmq"
  ZMQ_PREFIX="/usr/local"

  if ! pip3 list | grep -F pyzmq >> /dev/null; then
    cd ${HOME} && mkdir ${ZMQ_TMP_DIR} && cd ${ZMQ_TMP_DIR}
    # Download pre-compiled libzmq armv6 from Google Drive
    # https://drive.google.com/file/d/1KP6BqLF-i2dCUsHhOUpOwwuOmKsB5GKY/view?usp=sharing
    wget --quiet --load-cookies /tmp/cookies.txt "https://docs.google.com/uc?export=download&confirm=$(wget --quiet --save-cookies /tmp/cookies.txt --keep-session-cookies --no-check-certificate 'https://docs.google.com/uc?export=download&id=1KP6BqLF-i2dCUsHhOUpOwwuOmKsB5GKY' -O- | sed -rn 's/.*confirm=([0-9A-Za-z_]+).*/\1\n/p')&id=1KP6BqLF-i2dCUsHhOUpOwwuOmKsB5GKY" -O libzmq.tar.gz && rm -rf /tmp/cookies.txt
    tar -xzf libzmq.tar.gz
    rm -f libzmq.tar.gz
    sudo rsync -a * ${ZMQ_PREFIX}/

    pip3 install -q --pre pyzmq \
      --install-option=--enable-drafts \
      --install-option=--zmq=${ZMQ_PREFIX}
  else
    echo "      Skipping. pyzmq already installed"
  fi

  echo "    Install requirements"
  cd ${INSTALLATION_DIR}
  pip3 install -q --no-cache-dir -r ${INSTALLATION_DIR}/requirements.txt

  # Install Node dependencies
  # TODO: Avoid building the app locally
  # Instead implement a Github Action that prebuilds on commititung a git tag
  echo "  Install web application"
  cd ${INSTALLATION_DIR}/src/webapp
  npm install --production --silent
  rm -rf build
  npm run build

  calc_runtime_and_print time_start $(date +%s)
}

# Samba configuration settings
configure_samba() {
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
  path=${INSTALLATION_DIR}/shared
  browseable=Yes
  writeable=Yes
  only guest=no
  create mask=0777
  directory mask=0777
  public=no
EOF

    sudo chmod 644 $SMB_CONF
  fi
}

register_jukebox_settings() {
  echo "Register Jukebox settings" | tee /dev/fd/3

  # TODO
  # Ask for Jukebox Name
  # Ask for Jukebox hostname to replace raspberry.local

  cp -f ${INSTALLATION_DIR}/resources/default-settings/jukebox.default.yaml ${SETTINGS_DIR}/jukebox.yaml
}

register_system_services() {
  local time_start=$(date +%s)

  echo "Register system services" | tee /dev/fd/3
  sudo cp -f ${INSTALLATION_DIR}/resources/default-services/jukebox-*.service /lib/systemd/system
  sudo chmod 644 /lib/systemd/system/jukebox-*.service

  sudo systemctl enable jukebox-daemon.service
  sudo systemctl enable jukebox-webapp.service

  sudo systemctl daemon-reload

  echo "Configure MPD"
  # TODO: Could this be read from the jukebox.yaml?
  local mpd_conf_path = "${SETTINGS_DIR}/mpd.conf"
  local audiofolders_path = "${SHARED_DIR}/audiofolders"
  local playlists_path = "${SHARED_DIR}/playlists"
  local alsa_mixer_control = "Headphone"

  sudo systemctl stop mpd.service

  # Prepare new mpd.conf
  sudo cp -f ${INSTALLATION_DIR}/resources/default-settings/mpd.default.conf ${mpd_conf_path}
  sudo sed -i 's/%%JUKEBOX_AUDIOFOLDERS_PATH%%/'"$audiofolders_path"'/' ${mpd_conf_path}
  sudo sed -i 's/%%JUKEBOX_PLAYLISTS_PATH%%/'"$audiofolders_path"'/' ${mpd_conf_path}
  sudo sed -i 's/%%JUKEBOX_ALSA_MIXER_CONTROL%%/'"$alsa_mixer_control"'/' ${mpd_conf_path}

  # Reload mpd
  # Make original file unreachable
  sudo cp -f /etc/mpd.conf /etc/mpd.conf.orig
  # Update mpd.service file to use Jukebox mpd.conf
  sudo sed -i 's/$MPDCONF/'"$mpd_conf_path"'/' /lib/systemd/system/mpd.service
  sudo systemctl daemon-reload
  sudo systemctl start mpd.service
  mpc update

  # We don't start the services now, we wait for the reboot
  calc_runtime_and_print time_start $(date +%s)
}

finish() {
  echo "Installation complete!

In order to start, you need to reboot your Raspberry Pi.
Thi will disconnect your SSH connection.

Then you can open http://raspberrypi.local in your browser
to get started. Don't forget to upload files via Samba.

Do you want to reboot now? [Y/n]" 1>&3

  read -rp "Do you want to install? [Y/n] " response
  case "$response" in
    [nN][oO]|[nN])
      exit
      ;;
    *)
      echo "Rebooting ..." 1>&3
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
  configure_samba
  install_jukebox
  register_jukebox_settings
  register_system_services

  calc_runtime_and_print time_start $(date +%s)

  finish
}

### RUN INSTALLATION

# Log installation for debugging reasons
INSTALLATION_LOGFILE="$HOME_DIR/INSTALL-$INSTALL_ID.log"
# Source: https://stackoverflow.com/questions/18460186/writing-outputs-to-log-file-and-console
exec 3>&1 1>>${INSTALLATION_LOGFILE} 2>&1
echo "Log start: $INSTALL_ID"

install
