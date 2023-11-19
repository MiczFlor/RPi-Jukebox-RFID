#!/usr/bin/env bash

update_raspi_os() {
    if [ "$UPDATE_RASPI_OS" == true ] ; then
        echo "Updating Raspberry Pi OS" | tee /dev/fd/3

        sudo apt-get -qq -y update && sudo apt-get -qq -y full-upgrade && sudo apt-get -qq -y autoremove || exit_on_error "Failed to Update Raspberry Pi OS"

        echo "DONE: update_raspi_os"
    fi
}
