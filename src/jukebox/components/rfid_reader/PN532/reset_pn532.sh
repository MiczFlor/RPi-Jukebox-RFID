#!/usr/bin/env bash

printf "Stopping phoniebox-rfid-reader service...\n"
sudo systemctl stop phoniebox-rfid-reader.service

printf "Switching I2C off and on again via raspi-config...\n"
sudo raspi-config nonint do_i2c 1 #off
sleep 10
sudo raspi-config nonint do_i2c 0 #on
#TODO: how to handle seg faults?

printf "Checking if PN532 RFID reader is found through I2C...\n"
if sudo i2cdetect -y 1 | grep "24" ; then
    printf "  PN532 was found.\n"
else
    printf "  ERROR: PN532 was not found.\n"
    # Run again to show possible error messages
    sudo i2cdetect -y 1
    exit 1
fi

printf "Starting phoniebox-rfid-reader service...\n"
sudo systemctl start phoniebox-rfid-reader.service

printf "Done.\n"