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

printf "Please make sure that the RC522 reader is wired up correctly to the GPIO ports before continuing...\n"
question "Continue"

printf "Installing Python requirements for RC522...\n"
sudo python3 -m pip install -q -r "${JUKEBOX_HOME_DIR}"/components/rfid-reader/RC522/requirements.txt

printf "Configure RFID reader in Phoniebox...\n"
cp "${JUKEBOX_HOME_DIR}"/scripts/Reader.py.experimental "${JUKEBOX_HOME_DIR}"/scripts/Reader.py
printf "MFRC522" > "${JUKEBOX_HOME_DIR}"/scripts/deviceName.txt
sudo chown pi:www-data "${JUKEBOX_HOME_DIR}"/scripts/deviceName.txt
sudo chmod 644 "${JUKEBOX_HOME_DIR}"/scripts/deviceName.txt

printf "Restarting phoniebox-rfid-reader service...\n"
sudo systemctl start phoniebox-rfid-reader.service

printf "Done.\n"
