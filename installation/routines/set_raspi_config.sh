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
}

set_raspi_config() {
    run_with_log_frame _run_set_raspi_config "Set default raspi-config"
}
