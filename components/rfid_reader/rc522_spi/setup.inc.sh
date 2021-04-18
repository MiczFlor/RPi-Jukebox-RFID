#!/usr/bin/env bash

echo "Entering setup.inc.sh"

printf "Activating SPI...\n"
sudo raspi-config nonint do_spi 0

echo -e "\nREBOOT for changes to take effect!\n"
