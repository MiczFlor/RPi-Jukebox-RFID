#!/usr/bin/env bash


set_raspi_config() {
  echo "Set default raspi-config" | tee /dev/fd/3
  # Source: https://raspberrypi.stackexchange.com/a/66939

  # Autologin
  echo "  * Enable Autologin for 'pi' user"
  sudo raspi-config nonint do_boot_behaviour B2

  # Wait for network at boot
  # echo "  * Enable 'Wait for network at boot'"
  # sudo raspi-config nonint do_boot_wait 1

  # power management of wifi: switch off to avoid disconnecting
  echo "  * Disable Wifi power management to avoid disconnecting"
  sudo iwconfig wlan0 power off

  # On-board audio
  if [[ $(get_onboard_audio) -eq 1 ]]; then
    DISABLE_ONBOARD_AUDIO=${DISABLE_ONBOARD_AUDIO:-false}
    if [[ $DISABLE_ONBOARD_AUDIO = true ]]; then
      echo "  * Disable on-chip BCM audio"
      echo "Backup ${RPI_BOOT_CONFIG_FILE} --> ${DISABLE_ONBOARD_AUDIO_BACKUP}"
      sudo cp "${RPI_BOOT_CONFIG_FILE}" "${DISABLE_ONBOARD_AUDIO_BACKUP}"
      sudo sed -i "s/^\(dtparam=\([^,]*,\)*\)audio=\(on\|true\|yes\|1\)\(.*\)/\1audio=off\4/g" "${RPI_BOOT_CONFIG_FILE}"
    fi
  else
    echo "On board audio seems to be off already. Not touching ${RPI_BOOT_CONFIG_FILE}"
  fi

}
