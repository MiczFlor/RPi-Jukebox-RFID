#!/bin/bash
# DO NOT USE UNTIL THIS LINE HAS DISAPPEARED
#
# see https://github.com/MiczFlor/RPi-Jukebox-RFID for details
#
# sketch for a luxury one line install script

clear
echo "##################################################### 
#    ___  __ ______  _  __________ ____   __  _  _  #
#   / _ \/ // / __ \/ |/ /  _/ __/(  _ \ /  \( \/ ) #
#  / ___/ _  / /_/ /    // // _/   ) _ ((  O ))  (  #
# /_/  /_//_/\____/_/|_/___/____/ (____/ \__/(_/\_) #
#                                                   #
##################################################### 

Welcome to the installation script.


This script will install Phoniebox on your Raspberry Pi.
To do so, you must be online. The install script can 
automatically configure:

* WiFi settings (SSID, password and static IP)

All these are optional and can also be done later
manually.

If you are ready, hit ENTER"
read INPUT

##################################################### 
# CONFIG FILE
# This file will contain all the data given in the
# following dialogue
# At a later stage, the install should also be done
# from such a config file with no user input.

# Remove existing config file
rm PhonieboxInstall.conf
# Create empty config file
touch PhonieboxInstall.conf
echo "# Phoniebox config" > PhonieboxInstall.conf

##################################################### 
# Check for existing Phoniebox
# 
# later use of:
# shortcuts content
# audiofolders content
# card ID conf 
# GPIO file(s)
# Sounds startup shutdown

# move to home directory
cd
# check if Phoniebox folder exists
if [ -d RPi-Jukebox-RFID ]; then
    echo "WARNING: an existing Phoniebox installation was found."
    # YES, check if we find the version number
    if [ -f RPi-Jukebox-RFID/settings/version ]; then
        echo "The version of your installation is: $(cat RPi-Jukebox-RFID/settings/version)"
        echo "IMPORTANT: you can use the existing content and configuration files for your new install."
    fi
    # Delete or use existing installation?
    read -r -p "Do you want to use audiofiles, config and RFID codes for the new install? [Y/n] " response
    case "$response" in
        [nN][oO]|[nN])
    	    EXISTINGuse=NO
    	    echo "Phoniebox will be a fresh install. The existing version will be dropped."
    	    echo "Hit ENTER to proceed to the next step."
            #rm -r RPi-Jukebox-RFID
            read INPUT
            ;;
        *)
    	    EXISTINGuse=YES
            # CREATE BACKUP
            # delete existing BACKUP dir if exists
            if [ -d BACKUP ]; then
                sudo rm -r BACKUP
            fi
            # move install to BACKUP dir
            mv RPi-Jukebox-RFID BACKUP
            # delete .git dir
            if [ -d BACKUP/.git ]; then
                sudo rm -r BACKUP/.git
            fi
            # delete placeholder files so moving the folder content back later will not create git pull conflicts
            rm BACKUP/shared/audiofolders/placeholder
            rm BACKUP/shared/shortcuts/placeholder
            echo "The existing install can be found in the BACKUP directory."
            echo "Hit ENTER to proceed to the next step."
            read INPUT
            ;;
    esac
    # append variables to config file
    echo "EXISTINGuse=$EXISTINGuse" >> PhonieboxInstall.conf
fi

##################################################### 
# Ask if wifi config

clear

echo "#####################################################
#
# CONFIGURE WIFI
#
# Requires SSID, WiFi password and the static IP you want 
# to assign to your Phoniebox.
# (Note: can be done manually later, if you are unsure.)
"
read -r -p "Do you want to configure your WiFi? [Y/n] " response
case "$response" in
    [nN][oO]|[nN])
    	WIFIconfig=NO
    	echo "You want to configure WiFi later."
    	echo "Hit ENTER to proceed to the next step."
        read INPUT
        # append variables to config file
        echo "WIFIconfig=$WIFIconfig" >> PhonieboxInstall.conf
        ;;
    *)
    	WIFIconfig=YES
        #Ask for ssid
        echo "* Type SSID name"
        read INPUT
        WIFIssid="$INPUT"
        #Ask for password
        echo "* Type password"
        read INPUT
        WIFIpass="$INPUT"
        #Ask for IP
        echo "* Static IP (e.g. 192.168.1.1)"
        read INPUT
        WIFIip="$INPUT"
        echo "Your WiFi config:"
        echo "SSID      : $WIFIssid"
        echo "Password  : $WIFIpass"
        echo "Static IP : $WIFIip"
        read -r -p "Are these values correct? [Y/n] " response
        case "$response" in
            [nN][oO]|[nN])
            	echo "The values are incorrect."
            	echo "Hit ENTER to exit and start over."
                read INPUT; exit
                ;;
            *)
                # append variables to config file
                echo "hello 1"
                echo -e "hello 1" >> PhonieboxInstall.conf
                echo WIFIconfig=$WIFIconfig >> PhonieboxInstall.conf
                echo "WIFIssid=$WIFIssid" >> PhonieboxInstall.conf
                echo "WIFIpass=$WIFIpass" >> PhonieboxInstall.conf
                echo "WIFIip=$WIFIip" >> PhonieboxInstall.conf
                echo "hello"
                ;;
        esac
        ;;
esac

                echo -e "hello 1" >> PhonieboxInstall.conf
                echo WIFIconfig=$WIFIconfig >> PhonieboxInstall.conf
                echo "WIFIssid=$WIFIssid" >> PhonieboxInstall.conf
                echo "WIFIpass=$WIFIpass" >> PhonieboxInstall.conf
                echo "WIFIip=$WIFIip" >> PhonieboxInstall.conf
exit
##################################################### 
# Ask if access point

clear

echo "#####################################################
#
# CONFIGURE ACCESS POINT
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
        read INPUT
        ;;
    *)
    	ACCESSconfig=YES
        ;;
esac


##################################################### 
# Configure MPD

clear
MPDconfig=YES

echo "#####################################################
#
# CONFIGURE MPD
#
# MPD (Music Player Daemon)  runs the audio output and must
# be configured. Do it now, if you are unsure.
# (Note: can be done manually later.)
"
read -r -p "Do you want to configure MPD? [Y/n] " response
case "$response" in
    [nN][oO]|[nN])
    	MPDconfig=NO
    	echo "You want to configure MPD later."
    	echo "Hit ENTER to proceed to the next step."
        read INPUT
        ;;
    *)
    	MPDconfig=YES
    	echo "MPD will be set up with default values."
    	echo "Hit ENTER to proceed to the next step."
        read INPUT
        ;;
esac

clear
echo "Good news: you completed the input. 
Let the install begin.

Get yourself a cup of something. The install takes 
between 15 minutes to half an hour, depending on 
your Raspberry Pi and Internet connectivity.

You will be prompted later to complete the installation.

Hit ENTER to start the installation."
read INPUT; clear


##################################################### 
# INSTALLATION

##############
# Access Point
# http://www.raspberryconnect.com/network/item/331-raspberry-pi-auto-wifi-hotspot-switch-no-internet-routing
# Remove dns-root-data
sudo apt-get purge dns-root-data
# Install packages
sudo apt-get install hostapd dnsmasq
# Stop running processes
sudo systemctl stop hostapd
sudo systemctl stop dnsmasq

echo "
########################
# Hotspot (Access Point)
NOTE:
The network 'phoniebox' appears only when away from your usual WiFi.
You can connect from any device with the password 'PlayItLoud'.
In your browser, open the IP '10.0.0.10' to access the web app.
"

# BACKUP conf files
# cp /etc/hostapd/hostapd.conf hostapd.conf.stretch.sample
# cp /etc/default/hostapd hostapd.stretch.sample
# cp /etc/dnsmasq.conf dnsmasq.conf.stretch.sample
# cp /etc/network/interfaces interfaces.stretch.sample

# / Access Point
################

# / INSTALLATION
##################################################### 

#Ask if Spotify config

#If Spotify
#Ask for user
#Ask for password

#Ask samba password
#Ask ssh password


# get existing install
# new config should be done with sed using existing conf and user input
# samba nad yss password iwthout prompt

# CLEANUP
## remove dir BACKUP (possibly not, because we od this ta the ebginning after user confirms for latest config)
