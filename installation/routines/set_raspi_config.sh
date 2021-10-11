#!/usr/bin/env bash

set_raspi_config() {
  echo "Set default raspi-config" | tee /dev/fd/3
  # Source: https://raspberrypi.stackexchange.com/a/66939

  # Autologin
  echo "  * Enable Autologin for 'pi' user" 1>&3
  sudo raspi-config nonint do_boot_behaviour B2

  # Wait for network at boot
  # echo "  * Enable 'Wait for network at boot'" 1>&3
  # sudo raspi-config nonint do_boot_wait 1

  # power management of wifi: switch off to avoid disconnecting
  echo "  * Disable Wifi power management to avoid disconnecting" 1>&3
  sudo iwconfig wlan0 power off
}
