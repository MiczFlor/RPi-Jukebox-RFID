#!/usr/bin/env bash

# TODO: Could this be read from the jukebox.yaml?
AUDIOFOLDERS_PATH="${SHARED_PATH}/audiofolders"
PLAYLISTS_PATH="${SHARED_PATH}/playlists"

# Do not change this directory! It must match MPDs expectation where to find the user configuration
MPD_CONF_PATH="$HOME/.config/mpd/mpd.conf"

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
  # MPD will be setup as user process (rather than a system-wide process)
  mkdir -p ~/.config/mpd

  cp -f "${INSTALLATION_PATH}/resources/default-settings/mpd.default.conf" "${MPD_CONF_PATH}"

  # Prepare new mpd.conf
  sed -i 's|%%JUKEBOX_AUDIOFOLDERS_PATH%%|'"$AUDIOFOLDERS_PATH"'|' "${MPD_CONF_PATH}"
  sed -i 's|%%JUKEBOX_PLAYLISTS_PATH%%|'"$PLAYLISTS_PATH"'|' "${MPD_CONF_PATH}"

  # Make the system-wide file unreachable (just in case)
  # sudo mv -f "${MPD_CONF_PATH}" "${MPD_CONF_PATH}.orig"

#  # Prepare new mpd.conf
#  sudo cp -f ${INSTALLATION_PATH}/resources/default-settings/mpd.default.conf ${MPD_CONF_PATH}
#  sudo sed -i 's|%%JUKEBOX_AUDIOFOLDERS_PATH%%|'"$AUDIOFOLDERS_PATH"'|' ${MPD_CONF_PATH}
#  sudo sed -i 's|%%JUKEBOX_PLAYLISTS_PATH%%|'"$PLAYLISTS_PATH"'|' ${MPD_CONF_PATH}
#  sudo sed -i 's|%%JUKEBOX_ALSA_MIXER_CONTROL%%|'"$ALSA_MIXER_CONTROL"'|' ${MPD_CONF_PATH}
#  sudo chown mpd:audio "${MPD_CONF_PATH}"
#  sudo chmod 640 "${MPD_CONF_PATH}"
}

setup_mpd() {
  echo "Install MPD" | tee /dev/fd/3

  local MPD_EXECUTE_INSTALL=true

  if [[ -f ${MPD_CONF_PATH} || -f ${SYSTEMD_PATH}/mpd.service ]]; then
    echo "  It seems there is a MPD already installed."
    echo "  Note: It is important that MPD runs as a user service!"
    echo "  Would you like to overwrite your configuration? [Y/n] " | tee /dev/fd/3
      read -r response
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
    # Make sure system-wide mpd is disabled
    sudo systemctl stop mpd.socket
    sudo systemctl stop mpd
    sudo systemctl disable mpd.socket
    sudo systemctl disable mpd
    _mpd_configure
    # Prepare user-service MPD to be started at next boot
    systemctl --user daemon-reload
    systemctl --user enable mpd.socket
    systemctl --user enable mpd
    systemctl --user start mpd.socket
    systemctl --user start mpd
  fi

  echo "DONE: setup_mpd"
}
