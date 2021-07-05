#!/usr/bin/env bash
# Handle language configuration
export LC_ALL=C

HOME_DIR="/home/pi"
INSTALLATION_DIR="${HOME_DIR}/RPi-Jukebox-RFID"
GIT_URL="https://github.com/MiczFlor/RPi-Jukebox-RFID.git"
GIT_BRANCH="future3/webapp"

# Log installation for debugging reasons
exec >> $HOME_DIR/INSTALL.log 2>&1

# Update pi config
# Source: https://raspberrypi.stackexchange.com/a/66939
# Autologin
sudo raspi-config nonint do_boot_behaviour B2
# Wait for network at boot
sudo raspi-config nonint do_boot_wait 1
# Switch off Bluetooth to save energy
sudo systemctl stop bluetooth

# Update System
echo "Updating Raspberry Pi. This will take a while ..."
sudo apt-get -qq -y update; sudo apt-get -qq -y full-upgrade > /dev/null; sudo apt-get -qq -y autoremove

# Install Dependencies
echo "Installing Jukebox dependencies packages"

# Some definitions
echo "samba-common samba-common/dhcp boolean false" | sudo debconf-set-selections # Skip interactive Samba WINS config dialog

sudo apt-get -qq -y update; sudo apt-get -qq -y install \
  at git wget \
  mpd mpc \
  mpg123 \
  samba samba-common-bin \
  python3 python3-dev python3-pip python3-mutagen python3-gpiozero \
  gcc \
  ffmpeg \
  alsa-tools \
  --no-install-recommends \
  --allow-downgrades \
  --allow-remove-essential \
  --allow-change-held-packages
sudo rm -rf /var/lib/apt/lists/*

# Install Python
echo "Installing Python"
sudo update-alternatives --install /usr/bin/python python /usr/bin/python3.7 1

# Install Node
echo "Installing NodeJS"
curl -sL https://deb.nodesource.com/setup_16.x | sudo -E bash -
sudo apt-get -qq -y install nodejs
sudo npm install --silent -g npm pm2 serve

# ZMQ
# Because the latest stable release of ZMQ does not support WebSockets
# we need to compile the latest version in Github
# As soon WebSockets support is stable in ZMQ, this can be removed
echo "Compile ZMQ"
ZMQ_VERSION="4.3.4"
ZMQ_PREFIX="/usr/local"
cd ${HOME_DIR} && mkdir libzmq && cd libzmq
# TODO: Official release fails to compile on RPi (RPi freezes) - check TEMP solution
# wget https://github.com/zeromq/libzmq/releases/download/v${ZMQ_VERSION}/zeromq-${ZMQ_VERSION}.tar.gz -O libzmq.tar.gz

# TEMP: A compiled version has been uploaded to Google Drive
# Once found a proper solution, this should be removed
# Download from Google Drive: https://medium.com/@acpanjan/download-google-drive-files-using-wget-3c2c025a8b99
wget --quiet --load-cookies /tmp/cookies.txt "https://docs.google.com/uc?export=download&confirm=$(wget --quiet --save-cookies /tmp/cookies.txt --keep-session-cookies --no-check-certificate 'https://docs.google.com/uc?export=download&id=1iMieMzIOY-mpm37SVrgdhpjeyHZJKIdI' -O- | sed -rn 's/.*confirm=([0-9A-Za-z_]+).*/\1\n/p')&id=1iMieMzIOY-mpm37SVrgdhpjeyHZJKIdI" -O libzmq.tar.gz && rm -rf /tmp/cookies.txt
tar -xzf libzmq.tar.gz

# TODO: Only required when ZMQ is compiled on RPi, currently disabled
# zeromq-${ZMQ_VERSION}/configure --prefix=${ZMQ_PREFIX} --enable-drafts
# make -j && make install
pip3 install setuptools # Required for the following command to work, not sure why
pip3 install -q --pre pyzmq --install-option=--enable-drafts --install-option=--zmq=bundled

# Install Jukebox
echo "Install Phoniebox"
cd ${HOME_DIR}
git clone ${GIT_URL} --branch "${GIT_BRANCH}"

# Install Python dependencies
echo "Install Python Dependencies"
pip3 install -q --no-cache-dir -r ${INSTALLATION_DIR}/requirements.txt

# Install Node dependencies
echo "Build Webapp"
cd ${INSTALLATION_DIR}/src/webapp
npm install --silent && npm install --silent react-scripts@3.4.1 -g
npm run build