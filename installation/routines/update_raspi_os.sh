#!/usr/bin/env bash

_run_update_raspi_os() {
    sudo apt-get -qq -y update && sudo apt-get -qq -y full-upgrade && sudo apt-get -qq -y autoremove || exit_on_error "Failed to Update Raspberry Pi OS"
}

update_raspi_os() {
    if [ "$UPDATE_RASPI_OS" == true ] ; then
        run_with_log_frame _run_update_raspi_os "Updating Raspberry Pi OS"
    fi
}
