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

printf "Please make sure that the PN532 reader is wired up correctly to the GPIO ports before continuing...\n"
question "Continue"

printf "Activating I2C interface...\n"
sudo raspi-config nonint do_i2c 0

printf "Installing i2c-tools...\n"
sudo apt-get -qq -y install i2c-tools

printf "Checking if PN532 RFID reader is found through I2C...\n"
if sudo i2cdetect -y 1 | grep "24" ; then
    printf "  PN532 was found.\n"
else
    printf "  ERROR: PN532 was not found.\n"
    # Run again to show possible error messages
    sudo i2cdetect -y 1
    exit 1
fi

printf "Installing Python requirements for PN532...\n"
sudo python3 -m pip install -q -r "${JUKEBOX_HOME_DIR}"/components/rfid-reader/PN532/requirements.txt

printf "Configure RFID reader in Phoniebox...\n"
cp "${JUKEBOX_HOME_DIR}"/scripts/Reader.py.experimental "${JUKEBOX_HOME_DIR}"/scripts/Reader.py
printf "PN532" > "${JUKEBOX_HOME_DIR}"/scripts/deviceName.txt
sudo chown pi:www-data "${JUKEBOX_HOME_DIR}"/scripts/deviceName.txt
sudo chmod 644 "${JUKEBOX_HOME_DIR}"/scripts/deviceName.txt

printf "Restarting phoniebox-rfid-reader service...\n"
sudo systemctl start phoniebox-rfid-reader.service

printf "Done.\n"
