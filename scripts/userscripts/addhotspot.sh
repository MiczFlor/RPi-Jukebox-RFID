#!/bin/bash

# addhotspot.sh newssid newpassword
wpa_passphrase "$1" $2 >> /etc/wpa_supplicant/wpa_supplicant.conf

# /etc/dhcpcd.conf
echo ssid $1 >> /etc/dhcpcd.conf



