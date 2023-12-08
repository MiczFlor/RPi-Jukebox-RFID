#!/usr/bin/env bash

_run_setup_rfid_reader() {
    python "${INSTALLATION_PATH}/src/jukebox/run_register_rfid_reader.py" | log
}

setup_rfid_reader() {
    if [ "$ENABLE_RFID_READER" == true ] ; then
        run_with_log_frame _run_setup_rfid_reader "Install RFID Reader"
    fi
}
