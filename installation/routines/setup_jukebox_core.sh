#!/usr/bin/env bash

JUKEBOX_SERVICE_NAME="${SYSTEMD_USR_PATH}/jukebox-daemon.service"

_jukebox_core_install_python_requirements() {
  print_lc "  Install Python requirements"

  cd "${INSTALLATION_PATH}" || exit_on_error

  if [[ -d "${VIRTUAL_ENV}" ]]; then
    python3 -m venv --upgrade --system-site-packages "${VIRTUAL_ENV}"
  else
    python3 -m venv --system-site-packages "${VIRTUAL_ENV}"
  fi
  source "$VIRTUAL_ENV/bin/activate"

  # Older installations put a draft-enabled PyZMQ inside the venv. Inspect
  # package metadata instead of importing zmq so a broken native extension can
  # still be removed and Debian's python3-zmq package takes precedence.
  local pyzmq_path
  pyzmq_path=$(python -c \
    'from importlib.metadata import distribution; print(distribution("pyzmq").locate_file(""))' \
    2>/dev/null || true)
  if [[ "${pyzmq_path}" == "${VIRTUAL_ENV}/"* ]]; then
    python -m pip uninstall -y pyzmq
  fi

  # Build tooling is needed for native Python dependencies, but is not part of
  # the Jukebox runtime requirements.
  pip install --upgrade pip setuptools wheel
  # Remove excluded libs, if installed - see https://github.com/MiczFlor/RPi-Jukebox-RFID/pull/2470
  pip uninstall -y -r "${INSTALLATION_PATH}"/requirements-excluded.txt

  pip install --no-cache-dir -r "${INSTALLATION_PATH}/requirements.txt"
}

_jukebox_core_check_zmq() {
    log "  Verify standard ZMQ TCP and inproc transports"
    if ! python "${INSTALLATION_PATH}/ci/installation/zmq_smoke.py"; then
        exit_on_error "ERROR: Standard ZMQ transport smoke test failed!"
    fi
    log "  CHECK"
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

    _jukebox_core_check_zmq

    verify_files_chown "${CURRENT_USER}" "${CURRENT_USER_GROUP}" "${SETTINGS_PATH}/jukebox.yaml"
    verify_files_chown "${CURRENT_USER}" "${CURRENT_USER_GROUP}" "${SETTINGS_PATH}/logger.yaml"

    verify_files_chown root root "${SYSTEMD_USR_PATH}/jukebox-daemon.service"

    verify_file_contains_string "${INSTALLATION_PATH}" "${JUKEBOX_SERVICE_NAME}"

    verify_service_enablement jukebox-daemon.service enabled --user
}

_run_setup_jukebox_core() {
    _jukebox_core_install_python_requirements
    _jukebox_core_install_settings
    _jukebox_core_register_as_service
    _jukebox_core_check
}

setup_jukebox_core() {
    run_with_log_frame _run_setup_jukebox_core "Install Jukebox Core"
}
