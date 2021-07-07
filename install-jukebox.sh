#!/usr/bin/env bash
# Handle language configuration
export LC_ALL=C

# Constants
INSTALL_ID=$(date +%s)
HOME_DIR="/home/pi"
INSTALLATION_DIR="${HOME_DIR}/RPi-Jukebox-RFID"
GIT_URL="https://github.com/MiczFlor/RPi-Jukebox-RFID.git"
GIT_BRANCH="future3/webapp"

### Method definitions
# Welcome Screen
welcome() {
  clear
  echo "#####################################################
#    ___  __ ______  _  __________ ____   __  _  _  #
#   / _ \/ // / __ \/ |/ /  _/ __/(  _ \ /  \( \/ ) #
#  / ___/ _  / /_/ /    // // _/   ) _ ((  O ))  (  #
# /_/  /_//_/\____/_/|_/___/____/ (____/ \__/(_/\_) #
# future3                                           #
#####################################################

You are turning your Raspberry Pi into a Phoniebox. Good choice!
Do you want to install? [Y/n]" 1>&3

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
  sudo raspi-config nonint do_boot_behaviour B2
  # Wait for network at boot
  sudo raspi-config nonint do_boot_wait 1
  # power management of wifi: switch off to avoid disconnecting
  sudo iwconfig wlan0 power off
  # Switch off Bluetooth to save energy
  sudo systemctl stop bluetooth
  # Skip interactive Samba WINS config dialog
  echo "samba-common samba-common/dhcp boolean false" | sudo debconf-set-selections
}

# Update System
update_os() {
  echo "Updating Raspberry Pi OS" | tee /dev/fd/3
  sudo apt-get -qq -y update; sudo apt-get -qq -y full-upgrade > /dev/null; sudo apt-get -qq -y autoremove > /dev/null
}

# Install Dependencies
install_jukebox_dependencies() {
  echo "Install Jukebox OS dependencies" | tee /dev/fd/3
  sudo apt-get -qq -y update; sudo apt-get -qq -y install \
    at git wget \
    mpd mpc \
    mpg123 \
    samba samba-common-bin \
    python3 python3-dev python3-pip python3-mutagen python3-gpiozero \
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
    echo "  Found existing NodeJS. Hence, updating NodeJS" | tee /dev/fd/3
    sudo npm cache clean -f
    sudo n --quiet latest
    sudo npm update --silent -g
  else
    echo "  Install NodeJS" | tee /dev/fd/3
    curl -sL https://deb.nodesource.com/setup_16.x | sudo -E bash -
    sudo apt-get -qq -y install nodejs
    sudo npm install --silent -g n npm pm2 serve
  fi
}

# Install Jukebox
install_jukebox() {
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
      echo "  Updating version" | tee /dev/fd/3
      git pull
    fi
  else
    git clone ${GIT_URL} --branch "${GIT_BRANCH}"
  fi

  # Install Python dependencies
  echo "  Install Python dependencies" | tee /dev/fd/3
  # ZMQ
  # Because the latest stable release of ZMQ does not support WebSockets
  # we need to compile the latest version in Github
  # As soon WebSockets support is stable in ZMQ, this can be removed
  echo "    Install pyzmq" | tee /dev/fd/3
  ZMQ_VERSION="4.3.4"
  ZMQ_PREFIX="/usr/local"

  if ! pip3 list | grep -F pyzmq >> /dev/null; then
    cd ${HOME_DIR} && mkdir libzmq && cd libzmq
    # TODO: Official release fails to compile on RPi (RPi freezes) - check TEMP solution
    wget https://github.com/zeromq/libzmq/releases/download/v${ZMQ_VERSION}/zeromq-${ZMQ_VERSION}.tar.gz -O libzmq.tar.gz

    # TEMP: A compiled version has been uploaded to Google Drive
    # Once found a proper solution, this should be removed
    # Download from Google Drive: https://medium.com/@acpanjan/download-google-drive-files-using-wget-3c2c025a8b99
    # wget --quiet --load-cookies /tmp/cookies.txt "https://docs.google.com/uc?export=download&confirm=$(wget --quiet --save-cookies /tmp/cookies.txt --keep-session-cookies --no-check-certificate 'https://docs.google.com/uc?export=download&id=1iMieMzIOY-mpm37SVrgdhpjeyHZJKIdI' -O- | sed -rn 's/.*confirm=([0-9A-Za-z_]+).*/\1\n/p')&id=1iMieMzIOY-mpm37SVrgdhpjeyHZJKIdI" -O libzmq.tar.gz && rm -rf /tmp/cookies.txt
    tar -xzf libzmq.tar.gz

    # TODO: Only required when ZMQ is compiled on RPi, currently disabled
    zeromq-${ZMQ_VERSION}/configure --prefix=${ZMQ_PREFIX} --enable-drafts
    make -j && make install
    pip3 install -q setuptools # Required for the following command to work, not sure why
    pip3 install -q --pre pyzmq --install-option=--enable-drafts --install-option=--zmq=bundled
  else
    echo "    Skipping. pyzmq already installed" | tee /dev/fd/3
  fi
  pip3 install -q --no-cache-dir -r ${INSTALLATION_DIR}/requirements.txt

  # Install Node dependencies
  # TODO: Avoid building the app locally
  # Instead implement a Github Action that prebuilds on commititung a git tag
  echo "  Install web application" | tee /dev/fd/3
  cd ${INSTALLATION_DIR}/src/webapp
  npm install --production --silent
  rm -rf build
  npm run build
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

# if the audiofiles are not in 'shared', we need this
[phoniebox_audiofiles]
  comment= Pi Jukebox
  path=${INSTALLATION_DIR}/shared/audiofolders
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

main() {
  welcome
  set_raspi_config
  # update_os
  install_jukebox_dependencies
  configure_samba
  install_jukebox
}

### RUN INSTALLATION

# Log installation for debugging reasons
INSTALLATION_LOGFILE="$HOME_DIR/INSTALL-$INSTALL_ID.log"
# Source: https://stackoverflow.com/questions/18460186/writing-outputs-to-log-file-and-console
exec 3>&1 1>>${INSTALLATION_LOGFILE} 2>&1
echo "Log start: $INSTALL_ID"

start=$(date +%s)

main

end=$(date +%s)
runtime=$((end-start))
((h=${runtime}/3600))
((m=(${runtime}%3600)/60))
((s=${runtime}%60))

echo "Installation done in ${h}h ${m}m ${s}s." | tee /dev/fd/3
echo "Open http://raspberrypi.local in your browser to get started." 1>&3
