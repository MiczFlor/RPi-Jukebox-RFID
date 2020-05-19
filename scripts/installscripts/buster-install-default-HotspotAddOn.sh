#!/bin/bash

local apt_get="sudo apt-get -qq --yes"

#####################################################
# Ask if access point

clear 

echo "#####################################################
#
# CONFIGURE ACCESS POINT / HOTSPOT
#
# If you take your Phoniebox on the road and it is not
# connected to a WiFi network, it can automatically turn
# into an access point and show up as SSID 'phoniebox'.
# This will work for RPi3 out of the box. It might not
# work for other models and WiFi cards.
# (Note: can be done manually later, if you are unsure.)
"
read -rp "Do you want to configure as Access Point? [Y/n] " response
case "$response" in
    [nN][oO]|[nN])
        ACCESSconfig=NO
        echo "You don't want to configure as an Access Point."
        echo "Hit ENTER to proceed to the next step."
        read -r
        ;;
    *)
        ACCESSconfig=YES
        ;;
esac
# append variables to config file
# echo "ACCESSconfig=\"$ACCESSconfig\"" >> "${PATHDATA}/PhonieboxInstall.conf"


########################
# Access Point / Hotspot
# https://www.elektronik-kompendium.de/sites/raspberry-pi/2002171.htm
if [ "${ACCESSconfig}" == "YES" ]; then
   # debugging. Erase if productive
   # set -x
   
   # install requiered packages
   sudo apt-get install dnsmasq hostapd

   sudo echo -e "Added by RPi-Jukebox-RFID to enable this device as Hotspot" >> /etc/dhcpcd.conf
   sudo echo -e "interface wlan0" >> /etc/dhcpcd.conf
   sudo echo -e "static ip_address=192.168.99.1/24" >> /etc/dhcpcd.conf

   sudo systemctl restart dhcpcd
   
   # configure DNS
   sudo mv /etc/dnsmasq.conf /etc/dnsmasq.conf.orig
   sudo cat << EOF > /etc/dnsmasq.conf
# Activate DHCP-Server for WiFi-Interface
interface=wlan0

# Deactivate DHCP-Server for given interfaces
no-dhcp-interface=eth0

# IPv4-range and Lease-Time
dhcp-range=192.168.99.100,192.168.99.200,255.255.255.0,24h

# DNS
dhcp-option=option:dns-server,192.168.99.1
EOF
   dnsmasq --test -C /etc/dnsmasq.conf || exit 1
   sudo systemctl restart dnsmasq

   # configure hotspot
   sudo cat << EOF > /etc/hostapd/hostapd.conf
# WiFi Hotspot

# interface and driver
interface=wlan0
#driver=nl80211

# WiFi configuration
ssid=phoniebox
channel=1
hw_mode=g
ieee80211n=1
ieee80211d=1
country_code=DE
wmm_enabled=1

# WLAN-Verschlüsselung
auth_algs=1
wpa=2
wpa_key_mgmt=WPA-PSK
rsn_pairwise=CCMP
wpa_passphrase=PlayItLoud
EOF
   sudo chmod 600 /etc/hostapd/hostapd.conf
   
   sudo hostapd -dd /etc/hostapd/hostapd.conf || exit 2

   # configure Hotspot daemon
   sudo cat << EOF > /etc/default/hostapd
RUN_DAEMON=yes
DAEMON_CONF="/etc/hostapd/hostapd.conf"
EOF
   sudo systemctl unmask hostapd
   sudo systemctl start hostapd
   sudo systemctl enable hostapd

   echo "
   ########################
   # Hotspot (Access Point)
   NOTE:
   The network 'phoniebox' appears only when away from your usual WiFi.
   You can connect from any device with the password 'PlayItLoud'.
   "
fi
