#!/usr/bin/env bash

echo "Entering setup.inc.sh"

printf "Activating I2C interface...\n"
sudo raspi-config nonint do_i2c 0

echo -e "\nREBOOT for changes to take effect!\n"

