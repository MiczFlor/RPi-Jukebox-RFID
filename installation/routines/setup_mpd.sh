#!/usr/bin/env bash

AUDIOFOLDERS_PATH="${SHARED_PATH}/audiofolders"
PLAYLISTS_PATH="${SHARED_PATH}/playlists"

_mpd_install_os_dependencies() {
  sudo apt-get -y update
  echo "Install MPD OS dependencies"
  echo "Note: Installing MPD might cause a message: 'Job failed. See journalctl -xe for details'"
  echo "It can be ignored! It's an artefact of the MPD installation - nothing we can do about it."
  sudo apt-get -y install \
    mpd mpc \
    --no-install-recommends \
    --allow-downgrades \
    --allow-remove-essential \
    --allow-change-held-packages
}

_mpd_configure() {
  # MPD will be setup as user process (rather than a system-wide process)
  mkdir -p $(dirname "$MPD_CONF_PATH")

  cp -f "${INSTALLATION_PATH}/resources/default-settings/mpd.default.conf" "${MPD_CONF_PATH}"

  # Prepare new mpd.conf
  sed -i 's|%%JUKEBOX_AUDIOFOLDERS_PATH%%|'"$AUDIOFOLDERS_PATH"'|' "${MPD_CONF_PATH}"
  sed -i 's|%%JUKEBOX_PLAYLISTS_PATH%%|'"$PLAYLISTS_PATH"'|' "${MPD_CONF_PATH}"
}

_mpd_check () {
    echo "Check MPD Installation" | tee /dev/fd/3
    verify_apt_packages mpd mpc

    verify_files_chmod_chown 755 "${CURRENT_USER}" "${CURRENT_USER_GROUP}" "${MPD_CONF_PATH}"

    verify_file_contains_string "${AUDIOFOLDERS_PATH}" "${MPD_CONF_PATH}"
    verify_file_contains_string "${PLAYLISTS_PATH}" "${MPD_CONF_PATH}"

    verify_service_enablement mpd.socket disabled
    verify_service_enablement mpd.service disabled

    verify_service_enablement mpd.socket enabled --user
    verify_service_enablement mpd.service enabled --user
}

setup_mpd() {
    if [ "$SETUP_MPD" == true ] ; then
        echo "Install MPD" | tee /dev/fd/3

        if [[ $ENABLE_MPD_OVERWRITE_INSTALL == true ]] ; then

            # Install/update only if enabled: do not stuff up any existing configuration
            _mpd_install_os_dependencies

            # Make sure system-wide mpd is disabled
            echo "Configure MPD as user local service" | tee /dev/fd/3
            sudo systemctl stop mpd.socket
            sudo systemctl stop mpd.service
            sudo systemctl disable mpd.socket
            sudo systemctl disable mpd.service
            _mpd_configure
            # Prepare user-service MPD to be started at next boot
            systemctl --user daemon-reload
            systemctl --user enable mpd.socket
            systemctl --user enable mpd.service

            _mpd_check
        fi

        echo "DONE: setup_mpd"
    fi
}
