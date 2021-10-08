#!/usr/bin/env bash

setup_mpd() {
  echo "Configure MPD" | tee /dev/fd/3
  # TODO: Could this be read from the jukebox.yaml?

  local AUDIOFOLDERS_PATH="${SHARED_PATH}/audiofolders"
  local PLAYLISTS_PATH="${SHARED_PATH}/playlists"
  local ALSA_MIXER_CONTROL="Headphone"

  sudo systemctl stop mpd.service

  local MPD_CONF_PATH="/etc/mpd.conf"
  if [ "$MPD_USE_DEFAULT_CONF_DIR" = true ] ; then
    # As an option, the mpd.conf can be located in the Jukebox installation path
    # TODO: If so done, also update the jukebox.yaml to point to the correct location!
    local MPD_CONF_PATH="${SETTINGS_PATH}/mpd.conf"
      # Update mpd.service file to use Jukebox mpd.conf
      sudo sed -i 's|$MPDCONF|'"$MPD_CONF_PATH"'|' ${SYSTEMD_PATH}/mpd.service
  fi

  # Make a backup of original file (and make it unreachable in case of non-default conf location)
  sudo mv -f /etc/mpd.conf /etc/mpd.conf.orig

  # Prepare new mpd.conf
  sudo cp -f ${INSTALLATION_PATH}/resources/default-settings/mpd.default.conf ${MPD_CONF_PATH}
  sudo sed -i 's|%%JUKEBOX_AUDIOFOLDERS_PATH%%|'"$AUDIOFOLDERS_PATH"'|' ${MPD_CONF_PATH}
  sudo sed -i 's|%%JUKEBOX_PLAYLISTS_PATH%%|'"$PLAYLISTS_PATH"'|' ${MPD_CONF_PATH}
  sudo sed -i 's|%%JUKEBOX_ALSA_MIXER_CONTROL%%|'"$ALSA_MIXER_CONTROL"'|' ${MPD_CONF_PATH}
  sudo chown mpd:audio "${MPD_CONF_PATH}"
  sudo chmod 640 "${MPD_CONF_PATH}"

  # Reload mpd
  sudo systemctl daemon-reload
  sudo systemctl start mpd.service
  mpc update

  echo "DONE: setup_mpd"
}
