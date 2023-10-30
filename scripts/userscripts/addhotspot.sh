#!/usr/bin/env bash

if [[ -z "$1" || -z "$2" ]]; then
    echo "usage: addhotspot.sh <ssid> <passphrase>"
	exit 1
fi

# addhotspot.sh newssid newpassword
wpa_passphrase "$1" $2 >> /etc/wpa_supplicant/wpa_supplicant.conf

# /etc/dhcpcd.conf
if [[ ! $(grep -w "ssid $1" /etc/dhcpcd.conf) ]]; then
    echo "ssid $1" >> /etc/dhcpcd.conf
fi
