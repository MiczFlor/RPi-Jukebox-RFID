#!/usr/bin/env bash

setup_jukebox_core() {
  local time_start=$(date +%s)

  echo "Install Jukebox Core dependencies" | tee /dev/fd/3
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


  echo "  Register Jukebox settings" | tee /dev/fd/3
  # TODO
  # Ask for Jukebox Name
  # Ask for Jukebox hostname to replace raspberry.local

  cp -f ${INSTALLATION_PATH}/resources/default-settings/jukebox.default.yaml ${SETTINGS_PATH}/jukebox.yaml
  cp -f ${INSTALLATION_PATH}/resources/default-settings/logger.default.yaml ${SETTINGS_PATH}/logger.yaml

  echo "  Register Core system service" | tee /dev/fd/3
  sudo cp -f ${INSTALLATION_PATH}/resources/default-services/jukebox-daemon.service ${SYSTEMD_PATH}
  sudo chmod 644 ${SYSTEMD_PATH}/jukebox-daemon.service

  sudo systemctl enable jukebox-daemon.service
  sudo systemctl daemon-reload

  calc_runtime_and_print time_start $(date +%s)
  echo "DONE: setup_jukebox_core"
}
