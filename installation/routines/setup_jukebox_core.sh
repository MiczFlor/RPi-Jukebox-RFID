#!/usr/bin/env bash

# Constants
GD_ID_COMPILED_LIBZMQ_ARMV7="1KP6BqLF-i2dCUsHhOUpOwwuOmKsB5GKY" # ARMv7: https://drive.google.com/file/d/1KP6BqLF-i2dCUsHhOUpOwwuOmKsB5GKY/view?usp=sharing
GD_ID_COMPILED_LIBZMQ_ARMV6="1tE8oaikl3LhX85ESrwyn3vHSpsW_wsTn" # ARMv6: https://drive.google.com/file/d/1tE8oaikl3LhX85ESrwyn3vHSpsW_wsTn/view?usp=sharing

# Helpers
_download_file_from_google_drive() {
  GD_SHARING_ID=${1}
  ZMQ_TAR_FILENAME=${2}
  wget --load-cookies /tmp/cookies.txt "https://docs.google.com/uc?export=download&confirm=$(wget --save-cookies /tmp/cookies.txt --keep-session-cookies --no-check-certificate 'https://docs.google.com/uc?export=download&id=${GD_SHARING_ID}' -O- | sed -rn 's/.*confirm=([0-9A-Za-z_]+).*/\1\n/p')&id=${GD_SHARING_ID}" -O ${ZMQ_TAR_FILENAME} && rm -rf /tmp/cookies.txt
  echo "Downloaded libzmq from Google Drive ID ${GD_SHARING_ID} into ${ZMQ_TAR_FILENAME}"
}

_show_slow_hardware_message() {
echo "  --------------------------------------------------------------------
  | Your hardware is a little slower so this step will take a while. |
  | Go watch a movie but don't let your computer go to sleep for the |
  | SSH connection to remain intact.                                 |
  --------------------------------------------------------------------" 1>&3
}

# Functions
_jukebox_core_install_os_dependencies() {
  echo "Install Jukebox OS dependencies"
  sudo apt-get -qq -y update; sudo apt-get -qq -y install \
    at git \
    alsa-tools \
    python3 python3-dev python3-pip python3-setuptools python3-mutagen python3-gpiozero \
    ffmpeg mpg123 \
    --no-install-recommends \
    --allow-downgrades \
    --allow-remove-essential \
    --allow-change-held-packages
}

_jukebox_core_install_python() {
  echo "  Install Python"
  sudo update-alternatives --install /usr/bin/python python /usr/bin/python3.7 1
}

_jukebox_core_install_pyzmq() {
  # ZMQ
  # Because the latest stable release of ZMQ does not support WebSockets
  # we need to compile the latest version in Github
  # As soon WebSockets support is stable in ZMQ, this can be removed
  # Sources:
  # https://pyzmq.readthedocs.io/en/latest/draft.html
  # https://github.com/MonsieurV/ZeroMQ-RPi/blob/master/README.md
  echo "  Install pyzmq"
  local ZMQ_TMP_PATH="libzmq"
  local ZMQ_PREFIX="/usr/local"
  local ZMQ_TAR_FILENAME="libzmq.tar.gz"

  if ! pip3 list | grep -F pyzmq >> /dev/null; then
    # Download pre-compiled libzmq from Google Drive because RPi has trouble compiling it
    echo "    Download pre-compiled libzmq from Google Drive because RPi has trouble compiling it"

    cd ${HOME_PATH} && mkdir ${ZMQ_TMP_PATH} && cd ${ZMQ_TMP_PATH}

    # ARMv7 as default
    LIBZMQ_GD_DOWNLOAD_ID=${GD_ID_COMPILED_LIBZMQ_ARMV7}
    if [ `uname -m` = "armv6l" ]; then
      # ARMv6 as fallback
      LIBZMQ_GD_DOWNLOAD_ID=${GD_ID_COMPILED_LIBZMQ_ARMV6}
      _show_slow_hardware_message
    fi

    _download_file_from_google_drive ${LIBZMQ_GD_DOWNLOAD_ID} ${ZMQ_TAR_FILENAME}
    tar -xzf ${ZMQ_TAR_FILENAME}
    rm -f ${ZMQ_TAR_FILENAME}
    sudo rsync -a * ${ZMQ_PREFIX}/

    pip3 install --pre pyzmq \
      --install-option=--enable-drafts \
      --install-option=--zmq=${ZMQ_PREFIX}
  else
    echo "    Skipping. pyzmq already installed"
  fi
}

_jukebox_core_install_python_requirements() {
  echo "  Install requirements"
  cd ${INSTALLATION_PATH}
  pip3 install --no-cache-dir -r ${INSTALLATION_PATH}/requirements.txt
}

_jukebox_core_install_settings() {
  echo "  Register Jukebox settings"
  cp -f ${INSTALLATION_PATH}/resources/default-settings/jukebox.default.yaml ${SETTINGS_PATH}/jukebox.yaml
  cp -f ${INSTALLATION_PATH}/resources/default-settings/logger.default.yaml ${SETTINGS_PATH}/logger.yaml
}

_jukebox_core_register_as_system_service() {
  echo "  Register Core system service"
  sudo cp -f ${INSTALLATION_PATH}/resources/default-services/jukebox-daemon.service ${SYSTEMD_PATH}
  sudo chmod 644 ${SYSTEMD_PATH}/jukebox-daemon.service

  sudo systemctl enable jukebox-daemon.service
  sudo systemctl daemon-reload
}

setup_jukebox_core() {
  echo "Install Jukebox Core" | tee /dev/fd/3

  _jukebox_core_install_os_dependencies
  _jukebox_core_install_python
  _jukebox_core_install_pyzmq
  _jukebox_core_install_python_requirements
  _jukebox_core_install_settings
  _jukebox_core_register_as_system_service

  echo "DONE: setup_jukebox_core"
}
