#!/usr/bin/env bash

# TODO: Could this be read from the jukebox.yaml?
AUDIOFOLDERS_PATH="${SHARED_PATH}/audiofolders"
PLAYLISTS_PATH="${SHARED_PATH}/playlists"
ALSA_MIXER_CONTROL="Headphone"
MPD_CONF_PATH="/etc/mpd.conf"

_mpd_install_os_dependencies() {
  echo "Install MPD OS dependencies"
  sudo apt-get -y update; sudo apt-get -y install \
    mpd mpc \
    --no-install-recommends \
    --allow-downgrades \
    --allow-remove-essential \
    --allow-change-held-packages
}

_mpd_configure() {
  # Make a backup of original file (and make it unreachable in case of non-default conf location)
  sudo mv -f ${MPD_CONF_PATH} ${MPD_CONF_PATH}.orig

  # Prepare new mpd.conf
  sudo cp -f ${INSTALLATION_PATH}/resources/default-settings/mpd.default.conf ${MPD_CONF_PATH}
  sudo sed -i 's|%%JUKEBOX_AUDIOFOLDERS_PATH%%|'"$AUDIOFOLDERS_PATH"'|' ${MPD_CONF_PATH}
  sudo sed -i 's|%%JUKEBOX_PLAYLISTS_PATH%%|'"$PLAYLISTS_PATH"'|' ${MPD_CONF_PATH}
  sudo sed -i 's|%%JUKEBOX_ALSA_MIXER_CONTROL%%|'"$ALSA_MIXER_CONTROL"'|' ${MPD_CONF_PATH}
  sudo chown mpd:audio "${MPD_CONF_PATH}"
  sudo chmod 640 "${MPD_CONF_PATH}"
}

_mpd_start_system_services() {
  sudo systemctl daemon-reload
  sudo systemctl start mpd.service
  mpc update
}

_mpd_stop_system_services() {
  sudo systemctl stop mpd.service
}

setup_mpd() {
  echo "Install MPD" | tee /dev/fd/3

  local MPD_EXECUTE_INSTALL=true

  if [[ -f ${MPD_CONF_PATH} || -f ${SYSTEMD_PATH}/mpd.service ]]; then
    echo "  It seems there is a MPD already installed."
    echo "  Would you like to overwrite your configuration? [Y/n] " | tee /dev/fd/3
      read -rp "MPD_OVERRIDE_CONFIG" response
      case "$response" in
        [nN][oO]|[nN])
          MPD_EXECUTE_INSTALL=false
          ;;
        *)
          ;;
      esac
  fi

  echo "MPD_EXECUTE_INSTALL=${MPD_EXECUTE_INSTALL}"

  _mpd_install_os_dependencies # Install or update anyways

  if [ "$MPD_EXECUTE_INSTALL" = true ] ; then
    _mpd_stop_system_services
    _mpd_configure
    _mpd_start_system_services
  fi

  echo "DONE: setup_mpd"
}
