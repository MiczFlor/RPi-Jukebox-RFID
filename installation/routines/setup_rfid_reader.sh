#!/usr/bin/env bash

setup_rfid_reader() {
    if [ "$ENABLE_RFID_READER" == true ] ; then
        echo "Install RFID Reader" | tee /dev/fd/3

        python "${INSTALLATION_PATH}/src/jukebox/run_register_rfid_reader.py" | tee /dev/fd/3

        echo "DONE: setup_rfid_reader"
    fi
}
