#!/usr/bin/env bash

HOME_DIR="/home/pi"
JUKEBOX_HOME_DIR="${HOME_DIR}/RPi-Jukebox-RFID"

question() {
    local question=$1
    read -p "${question} (y/n)? " choice
    case "$choice" in
      y|Y ) ;;
      n|N ) exit 0;;
      * ) echo "Error: invalid" ; question ${question};;
    esac
}

printf "Please make sure that the PC/SC reader is wired up correctly before continuing...\n"
question "Continue"

printf "Installing Python requirements for PC/SC reader...\n"
sudo python3 -m pip install --upgrade --force-reinstall -q -r "${JUKEBOX_HOME_DIR}"/components/rfid-reader/PC-SC/requirements.txt

printf "Configure RFID reader in Phoniebox...\n"
cp "${JUKEBOX_HOME_DIR}"/scripts/Reader.py.pcsc "${JUKEBOX_HOME_DIR}"/scripts/Reader.py
sudo python3 RegisterDevice.py

printf "Restarting phoniebox-rfid-reader service...\n"
sudo systemctl start phoniebox-rfid-reader.service

printf "Done.\n"
