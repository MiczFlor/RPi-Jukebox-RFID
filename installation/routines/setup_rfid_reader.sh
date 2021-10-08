#!/usr/bin/env bash

setup_rfid_reader() {
  local time_start=$(date +%s)

  python3 ${INSTALLATION_PATH}/src/jukebox/run_register_rfid_reader.py | tee /dev/fd/3

  calc_runtime_and_print time_start $(date +%s)
  echo "DONE: setup_rfid_reader"
}
