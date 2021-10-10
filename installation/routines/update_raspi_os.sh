#!/usr/bin/env bash

update_raspi_os() {
  echo "Updating Raspberry Pi OS" | tee /dev/fd/3

  sudo apt-get -qq -y update; sudo apt-get -qq -y full-upgrade; sudo apt-get -qq -y autoremove

  echo "DONE: update_raspi_os"
}
