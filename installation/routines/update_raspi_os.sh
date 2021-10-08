#!/usr/bin/env bash

update_raspi_os() {
  local time_start=$(date +%s)

  echo "Updating Raspberry Pi OS" | tee /dev/fd/3
  sudo apt-get -qq -y update; sudo apt-get -qq -y full-upgrade; sudo apt-get -qq -y autoremove

  calc_runtime_and_print time_start $(date +%s)
  echo "DONE: update_raspi_os"
}
