#!/usr/bin/env bash

echo "Entering setup.inc.sh"

echo "Disabling login shell to be accessible over serial"
sudo raspi-config nonint do_serial 1

echo "Enabling serial port hardware"
sudo raspi-config nonint set_config_var enable_uart 1 /boot/config.txt

echo -e "\nREBOOT for changes to take effect!\n"

