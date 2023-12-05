#!/usr/bin/env bash

# Constants
GD_ID_COMPILED_LIBZMQ_ARMV6="17VTgriCsYmAm72YKkga97jO0nExtq6G-" # armv6: https://drive.google.com/file/d/17VTgriCsYmAm72YKkga97jO0nExtq6G-/view?usp=sharing
GD_ID_COMPILED_LIBZMQ_ARMV7="1950psO7Mbs4GdWBMqIzdTAZPLnKhDg7F" # armv7: https://drive.google.com/file/d/1950psO7Mbs4GdWBMqIzdTAZPLnKhDg7F/view?usp=sharing
GD_ID_COMPILED_PYZMQ_ARMV6="1lDsV_pVcXbg6YReHb9AldMkyRZCpc6-n" # https://drive.google.com/file/d/1lDsV_pVcXbg6YReHb9AldMkyRZCpc6-n/view?usp=sharing
GD_ID_COMPILED_PYZMQ_ARMV7=""

ZMQ_TMP_DIR="libzmq"
ZMQ_PREFIX="/usr/local"

JUKEBOX_PULSE_CONFIG="${HOME_PATH}"/.config/pulse/default.pa
JUKEBOX_SERVICE_NAME="${SYSTEMD_USR_PATH}/jukebox-daemon.service"

_show_slow_hardware_message() {
echo "  --------------------------------------------------------------------
  | Your hardware is a little slower so this step will take a while. |
  | Go watch a movie but don't let your computer go to sleep for the |
  | SSH connection to remain intact.                                 |
  --------------------------------------------------------------------" 1>&3
}

# Functions
_jukebox_core_install_os_dependencies() {
  echo "  Install Jukebox OS dependencies" | tee /dev/fd/3

  local apt_packages=$(get_args_from_file "${INSTALLATION_PATH}/packages-core.txt")
  sudo apt-get -y update && sudo apt-get -y install \
    $apt_packages \
    --no-install-recommends \
    --allow-downgrades \
    --allow-remove-essential \
    --allow-change-held-packages
}

_jukebox_core_install_python_requirements() {
  echo "  Install Python requirements" | tee /dev/fd/3

  cd "${INSTALLATION_PATH}"  || exit_on_error

  python3 -m venv $VIRTUAL_ENV
  source "$VIRTUAL_ENV/bin/activate"

  pip install --upgrade pip
  pip install --no-cache-dir -r "${INSTALLATION_PATH}/requirements.txt"
}

_jukebox_core_configure_pulseaudio() {
  echo "  Copy PulseAudio configuration" | tee /dev/fd/3
  mkdir -p $(dirname "$JUKEBOX_PULSE_CONFIG")
  cp -f "${INSTALLATION_PATH}/resources/default-settings/pulseaudio.default.pa" "${JUKEBOX_PULSE_CONFIG}"
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

_jukebox_core_download_prebuilt_libzmq_with_drafts() {
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
  # https://pyzmq.readthedocs.io/en/latest/howto/draft.html
  # https://github.com/MonsieurV/ZeroMQ-RPi/blob/master/README.md
  echo "  Build and install pyzmq with WebSockets Support" | tee /dev/fd/3

  if ! pip list | grep -F pyzmq >> /dev/null; then
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
      _jukebox_core_download_prebuilt_libzmq_with_drafts
    fi

    ZMQ_PREFIX="${ZMQ_PREFIX}" ZMQ_DRAFT_API=1 \
      pip install --no-cache-dir --no-binary "pyzmq" --pre pyzmq
  else
    echo "    Skipping. pyzmq already installed" | tee /dev/fd/3
  fi
}

_jukebox_core_install_settings() {
  echo "  Register Jukebox settings" | tee /dev/fd/3
  cp -f "${INSTALLATION_PATH}/resources/default-settings/jukebox.default.yaml" "${SETTINGS_PATH}/jukebox.yaml"
  cp -f "${INSTALLATION_PATH}/resources/default-settings/logger.default.yaml" "${SETTINGS_PATH}/logger.yaml"
}

_jukebox_core_register_as_service() {
  echo "  Register Jukebox Core user service" | tee /dev/fd/3

  sudo cp -f "${INSTALLATION_PATH}/resources/default-services/jukebox-daemon.service" "${JUKEBOX_SERVICE_NAME}"
  sudo sed -i "s|%%INSTALLATION_PATH%%|${INSTALLATION_PATH}|g" "${JUKEBOX_SERVICE_NAME}"
  sudo chmod 644 "${JUKEBOX_SERVICE_NAME}"

  systemctl --user daemon-reload
  systemctl --user enable jukebox-daemon.service
}

_jukebox_core_check() {
    print_verify_installation

    local apt_packages=$(get_args_from_file "${INSTALLATION_PATH}/packages-core.txt")
    verify_apt_packages $apt_packages

    verify_dirs_exists "${VIRTUAL_ENV}"

    local pip_modules=$(get_args_from_file "${INSTALLATION_PATH}/requirements.txt")
    verify_pip_modules pyzmq $pip_modules

    verify_files_chmod_chown 644 "${CURRENT_USER}" "${CURRENT_USER_GROUP}" "${JUKEBOX_PULSE_CONFIG}"

    verify_files_chmod_chown 644 "${CURRENT_USER}" "${CURRENT_USER_GROUP}" "${SETTINGS_PATH}/jukebox.yaml"
    verify_files_chmod_chown 644 "${CURRENT_USER}" "${CURRENT_USER_GROUP}" "${SETTINGS_PATH}/logger.yaml"

    verify_files_chmod_chown 644 root root "${SYSTEMD_USR_PATH}/jukebox-daemon.service"

    verify_file_contains_string "${INSTALLATION_PATH}" "${JUKEBOX_SERVICE_NAME}"

    verify_service_enablement jukebox-daemon.service enabled --user
}

_run_setup_jukebox_core() {
    _jukebox_core_install_os_dependencies
    _jukebox_core_install_python_requirements
    _jukebox_core_configure_pulseaudio
    _jukebox_core_build_and_install_pyzmq
    _jukebox_core_install_settings
    _jukebox_core_register_as_service
    _jukebox_core_check
}

setup_jukebox_core() {
    run_with_log_frame _run_setup_jukebox_core "Install Jukebox Core"
}
