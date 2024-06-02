#!/usr/bin/env bash

AUDIOFOLDERS_PATH="${SHARED_PATH}/audiofolders"
PLAYLISTS_PATH="${SHARED_PATH}/playlists"

_mpd_install_os_dependencies() {
  log "  Install MPD OS dependencies"
  sudo apt-get -y update

  log "Note: Installing MPD might cause a message: 'Job failed. See journalctl -xe for details'
It can be ignored! It's an artefact of the MPD installation - nothing we can do about it."
  sudo apt-get -y install \
    mpd mpc \
    --no-install-recommends \
    --allow-downgrades \
    --allow-remove-essential \
    --allow-change-held-packages
}

_mpd_configure() {
  print_lc "  Configure MPD as user local service"

  # Make sure system-wide mpd is disabled
  sudo systemctl stop mpd.socket
  sudo systemctl stop mpd.service
  sudo systemctl disable mpd.socket
  sudo systemctl disable mpd.service
  # MPD will be setup as user process (rather than a system-wide process)
  mkdir -p $(dirname "$MPD_CONF_PATH")

  cp -f "${INSTALLATION_PATH}/resources/default-settings/mpd.default.conf" "${MPD_CONF_PATH}"

  # Prepare new mpd.conf
  sed -i 's|%%JUKEBOX_AUDIOFOLDERS_PATH%%|'"$AUDIOFOLDERS_PATH"'|' "${MPD_CONF_PATH}"
  sed -i 's|%%JUKEBOX_PLAYLISTS_PATH%%|'"$PLAYLISTS_PATH"'|' "${MPD_CONF_PATH}"

  # Prepare user-service MPD to be started at next boot
  systemctl --user daemon-reload
  systemctl --user enable mpd.socket
  systemctl --user enable mpd.service
}

_mpd_check() {
    print_verify_installation

    verify_apt_packages mpd mpc

    verify_files_chmod_chown 755 "${CURRENT_USER}" "${CURRENT_USER_GROUP}" "${MPD_CONF_PATH}"

    verify_file_contains_string "${AUDIOFOLDERS_PATH}" "${MPD_CONF_PATH}"
    verify_file_contains_string "${PLAYLISTS_PATH}" "${MPD_CONF_PATH}"

    verify_service_enablement mpd.socket disabled
    verify_service_enablement mpd.service disabled

    verify_service_enablement mpd.socket enabled --user
    verify_service_enablement mpd.service enabled --user
}

_run_setup_mpd() {
    _mpd_install_os_dependencies
    _mpd_configure
    _mpd_check
}

setup_mpd() {
    # Install/update only if enabled: do not stuff up any existing configuration
    if [[ "$SETUP_MPD" == true && $ENABLE_MPD_OVERWRITE_INSTALL == true ]] ; then
        run_with_log_frame _run_setup_mpd "Install MPD"
    fi
}
