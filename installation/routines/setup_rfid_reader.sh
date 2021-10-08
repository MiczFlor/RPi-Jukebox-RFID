#!/usr/bin/env bash

setup_rfid_reader() {
  python3 ${INSTALLATION_PATH}/src/jukebox/run_register_rfid_reader.py | tee /dev/fd/3

  echo "DONE: setup_rfid_reader"
}
