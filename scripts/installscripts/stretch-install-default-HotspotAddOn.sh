#!/bin/bash
# DO NOT USE UNTIL THIS LINE HAS DISAPPEARED
#
# This script turns the Phoniebox into a Hotspot
# IF there is no other WiFi network to connect to.
# Needs to run on top of a finished install. And might
# not work if you are not using a Pi3 or ZERO with Wifi.
# See for more information:
# http://www.raspberryconnect.com/network/item/331-raspberry-pi-auto-wifi-hotspot-switch-no-internet-routing
#
# Belongs to: https://github.com/chbuehlmann/RPi-Jukebox-RFID

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
read -r -p "Do you want to configure as Access Point? [Y/n] " response
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
echo "ACCESSconfig=\"$ACCESSconfig\"" >> "${PATHDATA}/PhonieboxInstall.conf"


########################
# Access Point / Hotspot
# http://www.raspberryconnect.com/network/item/331-raspberry-pi-auto-wifi-hotspot-switch-no-internet-routing
if [ $ACCESSconfig == "IGNOREFORNOWYES" ]
then

#
# NOT IMPLEMENTED YET
#
    # Work in progress, so keep in mind: BACKUP conf files for ACCESS POINT
    # cp /etc/hostapd/hostapd.conf hostapd.conf.stretch.sample
    # cp /etc/default/hostapd hostapd.stretch.sample
    # cp /etc/dnsmasq.conf dnsmasq.conf.stretch.sample
    # cp /etc/network/interfaces interfaces.stretch.sample
    # WIFIcountryCode
    # https://www.cisco.com/en/US/products/ps6305/products_configuration_guide_chapter09186a00804ddd8a.html

    # Remove dns-root-data
    sudo apt-get purge dns-root-data
    # Install packages
    sudo apt-get install hostapd dnsmasq iw
    # enter Y when prompted

    # The installers will have set up the programme so they run when the pi is started.
    # For this setup they only need to be started if the home router is not found.
    # So automatic startup needs to be disabled. This is done with the following commands:
    sudo systemctl disable hostapd
    sudo systemctl disable dnsmasq

    # -rw-r--r-- 1 root root 345 Aug 13 17:55 /etc/hostapd/hostapd.conf
    sudo cp /home/pi/RPi-Jukebox-RFID/misc/sampleconfigs/hostapd.conf.stretch-default2-Hotspot.sample /etc/hostapd/hostapd.conf
    sudo sed -i 's/%WIFIcountryCode%/'"$WIFIcountryCode"'/' /etc/hostapd/hostapd.conf
    sudo chmod 644 /etc/hostapd/hostapd.conf
    sudo chown root:root /etc/hostapd/hostapd.conf

    # -rw-r--r-- 1 root root 794 Aug 13 18:40 /etc/default/hostapd
    sudo cp /home/pi/RPi-Jukebox-RFID/misc/sampleconfigs/hostapd.stretch-default2-Hotspot.sample /etc/default/hostapd
    sudo chmod 644 /etc/default/hostapd
    sudo chown root:root /etc/default/hostapd

    # -rw-r--r-- 1 root root 82 Jul 17 15:13 /etc/network/interfaces
    sudo cp /home/pi/RPi-Jukebox-RFID/misc/sampleconfigs/interfaces.stretch-default2-Hotspot.sample /etc/network/interfaces
    sudo chmod 644 /etc/network/interfaces
    sudo chown root:root /etc/network/interfaces

    # DHCP configuration settings
    #-rw-rw-r-- 1 root netdev 0 Apr 17 11:25 /etc/dhcpcd.conf
    sudo cp /home/pi/RPi-Jukebox-RFID/misc/sampleconfigs/dhcpcd.conf.stretch-default2-Hotspot.sample /etc/dhcpcd.conf
    # Change IP for router and Phoniebox
    sudo sed -i 's/%WIFIip%/'"$WIFIip"'/' /etc/dhcpcd.conf
    sudo sed -i 's/%WIFIipRouter%/'"$WIFIipRouter"'/' /etc/dhcpcd.conf
    sudo sed -i 's/%WIFIcountryCode%/'"$WIFIcountryCode"'/' /etc/dhcpcd.conf
    # Change user:group and access mod
    sudo chown root:netdev /etc/dhcpcd.conf
    sudo chmod 664 /etc/dhcpcd.conf

    # /usr/bin/autohotspot
    sudo cp /home/pi/RPi-Jukebox-RFID/misc/sampleconfigs/autohotspot.stretch-default2-Hotspot.sample /usr/bin/autohotspot
    sudo chown root:root /usr/bin/autohotspot
    sudo chmod 644 /usr/bin/autohotspot
    sudo chmod +x /usr/bin/autohotspot

    # /etc/systemd/system/autohotspot.service
    sudo cp /home/pi/RPi-Jukebox-RFID/misc/sampleconfigs/autohotspot.service.stretch-default2-Hotspot.sample /etc/systemd/system/autohotspot.service
    sudo chown root:root /etc/systemd/system/autohotspot.service
    sudo chmod 644 /etc/systemd/system/autohotspot.service
    sudo systemctl enable autohotspot.service

    echo "
    ########################
    # Hotspot (Access Point)
    NOTE:
    The network 'phoniebox' appears only when away from your usual WiFi.
    You can connect from any device with the password 'PlayItLoud'.
    In your browser, open the IP '10.0.0.10' to access the web app.
    "
fi

# / Access Point
################
