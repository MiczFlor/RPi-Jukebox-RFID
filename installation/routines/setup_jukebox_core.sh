#!/usr/bin/env bash

# Constants
GD_ID_COMPILED_LIBZMQ_ARMV7="1KP6BqLF-i2dCUsHhOUpOwwuOmKsB5GKY" # ARMv7: https://drive.google.com/file/d/1KP6BqLF-i2dCUsHhOUpOwwuOmKsB5GKY/view?usp=sharing
GD_ID_COMPILED_LIBZMQ_ARMV6="1iygOm-G1cg_3YERuVRT6FhGBE34ZkwgV" # ARMv6: https://drive.google.com/file/d/1iygOm-G1cg_3YERuVRT6FhGBE34ZkwgV/view?usp=sharing
GD_ID_COMPILED_PYZMQ_ARMV7=""
GD_ID_COMPILED_PYZMQ_ARMV6="1lDsV_pVcXbg6YReHb9AldMkyRZCpc6-n" # https://drive.google.com/file/d/1lDsV_pVcXbg6YReHb9AldMkyRZCpc6-n/view?usp=sharing

ZMQ_TMP_DIR="libzmq"
ZMQ_PREFIX="/usr/local"

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
  sudo apt-get -y update; sudo apt-get -y install \
    at \
    alsa-utils \
    python3 python3-dev python3-pip python3-setuptools \
    python3-rpi.gpio python3-gpiozero \
    espeak ffmpeg mpg123 \
    pulseaudio pulseaudio-module-bluetooth pulseaudio-utils caps \
    --no-install-recommends \
    --allow-downgrades \
    --allow-remove-essential \
    --allow-change-held-packages

  sudo pip3 install --upgrade pip
}

_jukebox_core_configure_pulseaudio() {
  echo "Copy PulseAudio configuration"
  mkdir -p ~/.config/pulse
  cp -f "${INSTALLATION_PATH}/resources/default-settings/pulseaudio.default.pa" ~/.config/pulse/default.pa
}

_jukebox_core_build_libzmq_with_drafts() {
  LIBSODIUM_VERSION="1.0.18"
  ZMQ_VERSION="4.3.4"

  { cd "${HOME_PATH}" && mkdir "${ZMQ_TMP_DIR}" && cd "${ZMQ_TMP_DIR}"; } || exit_on_error
  wget --quiet https://github.com/jedisct1/libsodium/releases/download/${LIBSODIUM_VERSION}-RELEASE/libsodium-${LIBSODIUM_VERSION}.tar.gz
  tar -zxvf libsodium-${LIBSODIUM_VERSION}.tar.gz
  cd libsodium-${LIBSODIUM_VERSION} || exit_on_error
  ./configure
  make && make install

  cd "${HOME}/${ZMQ_TMP_DIR}" || exit_on_error
  wget https://github.com/zeromq/libzmq/releases/download/v${ZMQ_VERSION}/zeromq-${ZMQ_VERSION}.tar.gz -O libzmq.tar.gz
  tar -xzf libzmq.tar.gz
  zeromq-${ZMQ_VERSION}/configure --prefix=${ZMQ_PREFIX} --enable-drafts
  make && make install
}

_jukebox_core_download_prebuild_libzmq_with_drafts() {
  local ZMQ_TAR_FILENAME="libzmq.tar.gz"

  _download_file_from_google_drive "${LIBZMQ_GD_DOWNLOAD_ID}" "${ZMQ_TAR_FILENAME}"
  tar -xzf ${ZMQ_TAR_FILENAME}
  rm -f ${ZMQ_TAR_FILENAME}
  sudo rsync -a ./* ${ZMQ_PREFIX}/
}

_jukebox_core_build_and_install_pyzmq() {
  # ZMQ
  # Because the latest stable release of ZMQ does not support WebSockets
  # we need to compile the latest version in Github
  # As soon WebSockets support is stable in ZMQ, this can be removed
  # Sources:
  # https://pyzmq.readthedocs.io/en/latest/draft.html
  # https://github.com/MonsieurV/ZeroMQ-RPi/blob/master/README.md
  echo "  Build and install pyzmq with WebSockets Support"

  if ! sudo pip3 list | grep -F pyzmq >> /dev/null; then
    # Download pre-compiled libzmq from Google Drive because RPi has trouble compiling it
    echo "    Download pre-compiled libzmq from Google Drive because RPi has trouble compiling it"

    { cd "${HOME_PATH}" && mkdir "${ZMQ_TMP_DIR}" && cd "${ZMQ_TMP_DIR}"; } || exit_on_error

    # ARMv7 as default
    LIBZMQ_GD_DOWNLOAD_ID=${GD_ID_COMPILED_LIBZMQ_ARMV7}
    if [[ $(uname -m) == "armv6l" ]]; then
      # ARMv6 as fallback
      LIBZMQ_GD_DOWNLOAD_ID=${GD_ID_COMPILED_LIBZMQ_ARMV6}
      _show_slow_hardware_message
    fi

    if [ "$BUILD_LIBZMQ_WITH_DRAFTS_ON_DEVICE" = true ] ; then
      _jukebox_core_build_libzmq_with_drafts
    else
      _jukebox_core_download_prebuild_libzmq_with_drafts
    fi

    sudo pip3 install --pre pyzmq \
      --install-option=--enable-drafts \
      --install-option=--zmq=${ZMQ_PREFIX}
  else
    echo "    Skipping. pyzmq already installed"
  fi
}

_jukebox_core_download_prebuilt_pyzmq() {
  echo "  Download prebuilt pyzmq with WebSockets Support"
  local PYZMQ_TAR_FILENAME="pyzmq-build-armv6.tar.gz"

  cd "${HOME_PATH}" || exit_on_error

  # ARMv7 as default
  PYZMQ_GD_DOWNLOAD_ID=${GD_ID_COMPILED_PYZMQ_ARMV7}
  if [[ $(uname -m) == "armv6l" ]]; then
    # ARMv6 as fallback
    PYZMQ_GD_DOWNLOAD_ID=${GD_ID_COMPILED_PYZMQ_ARMV6}
  fi

  _download_file_from_google_drive "${PYZMQ_GD_DOWNLOAD_ID}" "${PYZMQ_TAR_FILENAME}"
  tar -xvf "${PYZMQ_TAR_FILENAME}" -C /
  rm -f "${PYZMQ_TAR_FILENAME}"
}

_jukebox_core_install_python_requirements() {
  echo "  Install requirements"
  cd "${INSTALLATION_PATH}"  || exit_on_error
  sudo pip3 install --no-cache-dir -r "${INSTALLATION_PATH}/requirements.txt"
}

_jukebox_core_install_settings() {
  echo "  Register Jukebox settings"
  cp -f "${INSTALLATION_PATH}/resources/default-settings/jukebox.default.yaml" "${SETTINGS_PATH}/jukebox.yaml"
  cp -f "${INSTALLATION_PATH}/resources/default-settings/logger.default.yaml" "${SETTINGS_PATH}/logger.yaml"
}

_jukebox_core_register_as_service() {
  echo "  Register Jukebox Core user service"
  sudo cp -f "${INSTALLATION_PATH}/resources/default-services/jukebox-daemon.service" "${SYSTEMD_USR_PATH}"
  sudo chmod 644 "${SYSTEMD_USR_PATH}/jukebox-daemon.service"

  systemctl --user daemon-reload
  systemctl --user enable jukebox-daemon.service
}

setup_jukebox_core() {
  echo "Install Jukebox Core" | tee /dev/fd/3

  _jukebox_core_install_os_dependencies
  _jukebox_core_configure_pulseaudio
  _jukebox_core_install_python_requirements
  _jukebox_core_build_and_install_pyzmq
  _jukebox_core_install_settings
  _jukebox_core_register_as_service

  echo "DONE: setup_jukebox_core"
}
