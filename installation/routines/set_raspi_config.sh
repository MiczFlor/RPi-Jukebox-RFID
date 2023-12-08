#!/usr/bin/env bash

_run_set_raspi_config() {
  # Source: https://raspberrypi.stackexchange.com/a/66939

  # Autologin
  log "  Enable Autologin for user"
  sudo raspi-config nonint do_boot_behaviour B2

  # Wait for network at boot
  # log "  Enable 'Wait for network at boot'"
  # sudo raspi-config nonint do_boot_wait 1

  # power management of wifi: switch off to avoid disconnecting
  log "  Disable Wifi power management to avoid disconnecting"
  sudo iwconfig wlan0 power off

  # On-board audio
  if [ "$DISABLE_ONBOARD_AUDIO" == true ]; then
    log "  Disable on-chip BCM audio"
    if grep -q -E "^dtparam=([^,]*,)*audio=(on|true|yes|1).*" "${RPI_BOOT_CONFIG_FILE}" ; then
      log "    Backup ${RPI_BOOT_CONFIG_FILE} --> ${DISABLE_ONBOARD_AUDIO_BACKUP}"
      sudo cp "${RPI_BOOT_CONFIG_FILE}" "${DISABLE_ONBOARD_AUDIO_BACKUP}"
      sudo sed -i "s/^\(dtparam=\([^,]*,\)*\)audio=\(on\|true\|yes\|1\)\(.*\)/\1audio=off\4/g" "${RPI_BOOT_CONFIG_FILE}"
    else
      log "    On board audio seems to be off already. Not touching ${RPI_BOOT_CONFIG_FILE}"
    fi
  fi
}

set_raspi_config() {
    run_with_log_frame _run_set_raspi_config "Set default raspi-config"
}
