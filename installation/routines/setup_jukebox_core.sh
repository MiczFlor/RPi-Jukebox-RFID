#!/usr/bin/env bash

# Constants
JUKEBOX_ZMQ_TMP_DIR="${HOME_PATH}/libzmq"
JUKEBOX_ZMQ_PREFIX="/usr/local"
JUKEBOX_ZMQ_VERSION="4.3.5"

JUKEBOX_PULSE_CONFIG="${HOME_PATH}"/.config/pulse/default.pa
JUKEBOX_SERVICE_NAME="${SYSTEMD_USR_PATH}/jukebox-daemon.service"

# Functions
_jukebox_core_install_os_dependencies() {
  print_lc "  Install Jukebox OS dependencies"

  local apt_packages=$(get_args_from_file "${INSTALLATION_PATH}/packages-core.txt")
  sudo apt-get -y update && sudo apt-get -y install \
    $apt_packages \
    --no-install-recommends \
    --allow-downgrades \
    --allow-remove-essential \
    --allow-change-held-packages
}

_jukebox_core_build_and_install_lgpio() {
    local tmp_path="${HOME_PATH}/tmp"
    local lg_filename="lg"
    local lg_zip_filename="${lg_filename}.zip"

    sudo apt-get -y install swig unzip python3-dev python3-setuptools
    mkdir -p "${tmp_path}" && cd "${tmp_path}" || exit_on_error
    download_from_url "http://abyz.me.uk/lg/${lg_zip_filename}" "${lg_zip_filename}"
    unzip ${lg_zip_filename} || exit_on_error
    cd "${lg_filename}" || exit_on_error
    make && sudo make install
    cd "${INSTALLATION_PATH}" && sudo rm -rf "${tmp_path}"
}

_jukebox_core_install_python_requirements() {
  print_lc "  Install Python requirements"

  cd "${INSTALLATION_PATH}" || exit_on_error

  python3 -m venv $VIRTUAL_ENV
  source "$VIRTUAL_ENV/bin/activate"

  pip install --upgrade pip
  # Remove excluded libs, if installed - see https://github.com/MiczFlor/RPi-Jukebox-RFID/pull/2470
  pip uninstall -y -r "${INSTALLATION_PATH}"/requirements-excluded.txt

  # prepare lgpio build for bullseye as the binaries are broken
  local pip_install_options=""
  if [ "$(is_debian_version_at_least 12)" = false ]; then
    _jukebox_core_build_and_install_lgpio
    pip_install_options="--no-binary=lgpio"
  fi

  pip install --no-cache-dir -r "${INSTALLATION_PATH}/requirements.txt" ${pip_install_options}
}

_jukebox_core_configure_pulseaudio() {
  print_lc "  Copy PulseAudio configuration"
  mkdir -p $(dirname "$JUKEBOX_PULSE_CONFIG")
  cp -f "${INSTALLATION_PATH}/resources/default-settings/pulseaudio.default.pa" "${JUKEBOX_PULSE_CONFIG}"
}

_jukebox_core_build_libzmq_with_drafts() {
  print_lc "    Building libzmq v${JUKEBOX_ZMQ_VERSION} with drafts support"
  local zmq_filename="zeromq-${JUKEBOX_ZMQ_VERSION}"
  local zmq_tar_filename="${zmq_filename}.tar.gz"
  local cpu_count=${CPU_COUNT:-$(python3 -c "import os; print(os.cpu_count())")}

  cd "${JUKEBOX_ZMQ_TMP_DIR}" || exit_on_error
  wget --quiet https://github.com/zeromq/libzmq/releases/download/v${JUKEBOX_ZMQ_VERSION}/${zmq_tar_filename} || exit_on_error "Download failed"
  tar -xzf ${zmq_tar_filename}
  rm -f ${zmq_tar_filename}
  cd ${zmq_filename} || exit_on_error
  ./configure --prefix=${JUKEBOX_ZMQ_PREFIX} --enable-drafts --disable-Werror
  make -j${cpu_count} && sudo make install
}

_jukebox_core_download_prebuilt_libzmq_with_drafts() {
  log "    Download pre-compiled libzmq with drafts support"
  local zmq_tar_filename="libzmq.tar.gz"
  ARCH=$(get_architecture)

  cd "${JUKEBOX_ZMQ_TMP_DIR}" || exit_on_error
  wget --quiet https://github.com/pabera/libzmq/releases/download/v${JUKEBOX_ZMQ_VERSION}/libzmq5-${ARCH}-${JUKEBOX_ZMQ_VERSION}.tar.gz -O ${zmq_tar_filename} || exit_on_error "Download failed"
  tar -xzf ${zmq_tar_filename}
  rm -f ${zmq_tar_filename}
  sudo rsync -a ./* ${JUKEBOX_ZMQ_PREFIX}/
}

_jukebox_core_build_and_install_pyzmq() {
  # ZMQ
  # Because the latest stable release of ZMQ does not support WebSockets
  # we need to compile the latest version in Github
  # As soon WebSockets support is stable in ZMQ, this can be removed
  # Sources:
  # https://pyzmq.readthedocs.io/en/latest/howto/draft.html
  # https://github.com/MonsieurV/ZeroMQ-RPi/blob/master/README.md
  # https://github.com/zeromq/pyzmq/issues/1523#issuecomment-1593120264
  print_lc "  Install pyzmq with libzmq-drafts to support WebSockets"

  if ! pip list | grep -F pyzmq >> /dev/null; then
    mkdir -p "${JUKEBOX_ZMQ_TMP_DIR}" || exit_on_error
    if [ "$BUILD_LIBZMQ_WITH_DRAFTS_ON_DEVICE" = true ] ; then
      _jukebox_core_build_libzmq_with_drafts
    else
      _jukebox_core_download_prebuilt_libzmq_with_drafts
    fi

    ZMQ_PREFIX="${JUKEBOX_ZMQ_PREFIX}" ZMQ_DRAFT_API=1 \
      pip install -v 'pyzmq<26' --no-binary pyzmq
  else
    print_lc "    Skipping. pyzmq already installed"
  fi
}

_jukebox_core_install_settings() {
  print_lc "  Register Jukebox settings"
  cp -f "${INSTALLATION_PATH}/resources/default-settings/jukebox.default.yaml" "${SETTINGS_PATH}/jukebox.yaml"
  cp -f "${INSTALLATION_PATH}/resources/default-settings/logger.default.yaml" "${SETTINGS_PATH}/logger.yaml"
}

_jukebox_core_register_as_service() {
  print_lc "  Register Jukebox Core user service"

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

    local pip_modules_excluded=$(get_args_from_file "${INSTALLATION_PATH}/requirements-excluded.txt")
    verify_pip_modules_not $pip_modules_excluded

    log "  Verify ZMQ version '${JUKEBOX_ZMQ_VERSION}'"
    local zmq_version=$(python -c 'import zmq; print(f"{zmq.zmq_version()}")')
    if [[ "${zmq_version}" != "${JUKEBOX_ZMQ_VERSION}" ]]; then
        exit_on_error "ERROR: ZMQ version '${zmq_version}' differs from expected '${JUKEBOX_ZMQ_VERSION}'!"
    fi
    log "  CHECK"

    log "  Verify ZMQ has 'DRAFT-API' activated"
    local zmq_hasDraftApi=$(python -c 'import zmq; print(f"{zmq.DRAFT_API}")')
    if [[ "${zmq_hasDraftApi}" != "True" ]]; then
        exit_on_error "ERROR: ZMQ has 'DRAFT-API' '${zmq_hasDraftApi}' differs from expected 'True'!"
    fi
    log "  CHECK"

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
    _jukebox_core_build_and_install_pyzmq
    _jukebox_core_configure_pulseaudio
    _jukebox_core_install_settings
    _jukebox_core_register_as_service
    _jukebox_core_check
}

setup_jukebox_core() {
    run_with_log_frame _run_setup_jukebox_core "Install Jukebox Core"
}
