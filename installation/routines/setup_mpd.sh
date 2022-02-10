#!/usr/bin/env bash

AUDIOFOLDERS_PATH="${SHARED_PATH}/audiofolders"
PLAYLISTS_PATH="${SHARED_PATH}/playlists"

# Do not change this directory! It must match MPDs expectation where to find the user configuration
MPD_CONF_PATH="$HOME/.config/mpd/mpd.conf"

_mpd_install_os_dependencies() {
  sudo apt-get -y update
  echo "Install MPD OS dependencies"
  echo "Note: Installing MPD will cause a message: 'Job failed. See journalctl -xe for details'"
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
  mkdir -p ~/.config/mpd

  cp -f "${INSTALLATION_PATH}/resources/default-settings/mpd.default.conf" "${MPD_CONF_PATH}"

  # Prepare new mpd.conf
  sed -i 's|%%JUKEBOX_AUDIOFOLDERS_PATH%%|'"$AUDIOFOLDERS_PATH"'|' "${MPD_CONF_PATH}"
  sed -i 's|%%JUKEBOX_PLAYLISTS_PATH%%|'"$PLAYLISTS_PATH"'|' "${MPD_CONF_PATH}"

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

  if [[ $MPD_EXECUTE_INSTALL == true ]] ; then

    # Install/update only if enabled: do not stuff up any existing configuration
    _mpd_install_os_dependencies

    # Make sure system-wide mpd is disabled
    echo "Configure MPD as user local service" | tee /dev/fd/3
    sudo systemctl stop mpd.socket
    sudo systemctl stop mpd
    sudo systemctl disable mpd.socket
    sudo systemctl disable mpd
    _mpd_configure
    # Prepare user-service MPD to be started at next boot
    systemctl --user daemon-reload
    systemctl --user enable mpd.socket
    systemctl --user enable mpd
    # Start MPD now, but not the socket: MPD is already started and we expect a reboot anyway
    systemctl --user start mpd
  fi

  echo "DONE: setup_mpd"
}
