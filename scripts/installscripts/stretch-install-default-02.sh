#!/bin/bash
# DO NOT USE UNTIL THIS LINE HAS DISAPPEARED
#
# see https://github.com/MiczFlor/RPi-Jukebox-RFID for details
#
# sketch for a luxury one line install script

# The absolute path to the folder which contains this script
PATHDATA="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

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
echo "# Phoniebox config" > $PATHDATA/PhonieboxInstall.conf

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
                echo "WIFIconfig=\"$WIFIconfig\"" >> $PATHDATA/PhonieboxInstall.conf
                echo "WIFIssid=\"$WIFIssid\"" >> $PATHDATA/PhonieboxInstall.conf
                echo "WIFIpass=\"$WIFIpass\"" >> $PATHDATA/PhonieboxInstall.conf
                echo "WIFIip=\"$WIFIip\"" >> $PATHDATA/PhonieboxInstall.conf
                ;;
        esac
        ;;
esac

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
# append variables to config file
echo "ACCESSconfig=\"$ACCESSconfig\"" >> $PATHDATA/PhonieboxInstall.conf

##################################################### 
# Configure MPD

clear

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
# append variables to config file
echo "MPDconfig=\"$MPDconfig\"" >> $PATHDATA/PhonieboxInstall.conf

clear
echo "Good news: you completed the input. 
Let the install begin.

Get yourself a cup of something. The install takes 
between 15 minutes to half an hour, depending on 
your Raspberry Pi and Internet connectivity.

You will be prompted later to complete the installation.
"

read -r -p "Do you want to start the installation? [Y/n] " response
case "$response" in
    [nN][oO]|[nN])
    	echo "Your configuration data was saved in this file:"
    	echo $PATHDATA/PhonieboxInstall.conf
    	echo "Hit ENTER to exit the install script."
    	read INPUT
        exit
        ;;
esac

##################################################### 
# INSTALLATION

# Read install config as written so far
# (this might look stupid so far, but makes sense once
# the option to install from config file is introduced.)
. $PATHDATA/PhonieboxInstall.conf

# Install required packages
sudo apt-get update
sudo apt-get install apt-transport-https samba samba-common-bin python-dev python-pip gcc linux-headers-4.9 lighttpd php7.0-common php7.0-cgi php7.0 php7.0-fpm at mpd mpc mpg123 git ffmpeg
sudo pip install "evdev == 0.7.0"
sudo pip install youtube_dl

# Get github code
cd /home/pi/
git clone https://github.com/MiczFlor/RPi-Jukebox-RFID.git

# Switch of WiFi power management
sudo iwconfig wlan0 power off

#####################################
# COPY CONFIG PRESETS TO LIVE FOLDERS
#####################################

# DHCP configuration settings
#-rw-rw-r-- 1 root netdev 0 Apr 17 11:25 /etc/dhcpcd.conf
sudo cp /home/pi/RPi-Jukebox-RFID/misc/sampleconfigs/dhcpcd.conf.stretch-default.sample /etc/dhcpcd.conf
sudo chown root:netdev /etc/dhcpcd.conf
sudo chmod 664 /etc/dhcpcd.conf

# Samba configuration settings
# -rw-r--r-- 1 root root 9416 Apr 30 09:02 /etc/samba/smb.conf
sudo cp /home/pi/RPi-Jukebox-RFID/misc/sampleconfigs/smb.conf.stretch-default.sample /etc/samba/smb.conf
sudo chown root:root /etc/samba/smb.conf
sudo chmod 644 /etc/samba/smb.conf

# Web server configuration settings
# -rw-r--r-- 1 root root 1040 Apr 30 09:19 /etc/lighttpd/lighttpd.conf
sudo cp /home/pi/RPi-Jukebox-RFID/misc/sampleconfigs/lighttpd.conf.stretch-default.sample /etc/lighttpd/lighttpd.conf
sudo chown root:root /etc/lighttpd/lighttpd.conf
sudo chmod 644 /etc/lighttpd/lighttpd.conf

# Web server PHP7 fastcgi conf
# -rw-r--r-- 1 root root 398 Apr 30 09:35 /etc/lighttpd/conf-available/15-fastcgi-php.conf
sudo cp /home/pi/RPi-Jukebox-RFID/misc/sampleconfigs/15-fastcgi-php.conf.stretch-default.sample /etc/lighttpd/conf-available/15-fastcgi-php.conf
sudo chown root:root /etc/lighttpd/conf-available/15-fastcgi-php.conf
sudo chmod 644 /etc/lighttpd/conf-available/15-fastcgi-php.conf

# SUDO users (adding web server here)
# -r--r----- 1 root root 703 Nov 17 21:08 /etc/sudoers
sudo cp /home/pi/RPi-Jukebox-RFID/misc/sampleconfigs/sudoers.jessie-default.sample /etc/sudoers
sudo chown root:root /etc/sudoers
sudo chmod 440 /etc/sudoers

# device name for barcode reader
# Note: this will vary from reader to reader. If you run this install script, 
# read 'Register your USB device for the jukebox' in docs/CONFIGURE-stretch.md to do this step manually
# -rw-r--r-- 1 pi pi 20 Nov 17 21:22 /home/pi/RPi-Jukebox-RFID/scripts/deviceName.txt
sudo cp /home/pi/RPi-Jukebox-RFID/misc/sampleconfigs/deviceName.txt.stretch-default.sample /home/pi/RPi-Jukebox-RFID/scripts/deviceName.txt
sudo chown pi:pi /home/pi/RPi-Jukebox-RFID/scripts/deviceName.txt
sudo chmod 644 /home/pi/RPi-Jukebox-RFID/scripts/deviceName.txt

# copy shell script for player
cp /home/pi/RPi-Jukebox-RFID/settings/rfid_trigger_play.conf.sample /home/pi/RPi-Jukebox-RFID/settings/rfid_trigger_play.conf
sudo chown pi:pi /home/pi/RPi-Jukebox-RFID/settings/rfid_trigger_play.conf
sudo chmod 775 /home/pi/RPi-Jukebox-RFID/settings/rfid_trigger_play.conf

# creating files containing editable values for configuration
# DISCONTINUED: now done by MPD? echo "PCM" > /home/pi/RPi-Jukebox-RFID/settings/Audio_iFace_Name
echo "PCM" > /home/pi/RPi-Jukebox-RFID/settings/Audio_iFace_Name
echo "3" > /home/pi/RPi-Jukebox-RFID/settings/Audio_Volume_Change_Step
echo "100" > /home/pi/RPi-Jukebox-RFID/settings/Max_Volume_Limit
echo "0" > /home/pi/RPi-Jukebox-RFID/settings/Idle_Time_Before_Shutdown

# make sure bash scripts have the right settings
sudo chown pi:pi /home/pi/RPi-Jukebox-RFID/scripts/*.sh
sudo chmod +x /home/pi/RPi-Jukebox-RFID/scripts/*.sh

# The new way of making the bash daemon is using the helperscripts 
# creating the shortcuts and script from a CSV file.
# see scripts/helperscripts/AssignIDs4Shortcuts.php

# create config file for web app from sample
sudo cp /home/pi/RPi-Jukebox-RFID/htdocs/config.php.sample /home/pi/RPi-Jukebox-RFID/htdocs/config.php

# make sure the shared folder is accessible by the web server
sudo chown -R pi:www-data /home/pi/RPi-Jukebox-RFID/shared
sudo chmod -R 775 /home/pi/RPi-Jukebox-RFID/shared

# make sure the htdocs folder can be changed by the web server
sudo chown -R pi:www-data /home/pi/RPi-Jukebox-RFID/htdocs
sudo chmod -R 775 /home/pi/RPi-Jukebox-RFID/htdocs

# Starting web server
sudo lighttpd-enable-mod fastcgi
sudo lighttpd-enable-mod fastcgi-php
sudo service lighttpd force-reload

# start DHCP
sudo service dhcpcd start
sudo systemctl enable dhcpcd

# services to launch after boot using systmed
# -rw-r--r-- 1 root root  304 Apr 30 10:07 rfid-reader.service
sudo cp /home/pi/RPi-Jukebox-RFID/misc/sampleconfigs/rfid-reader.service.stretch-default.sample /etc/systemd/system/rfid-reader.service 
sudo cp /home/pi/RPi-Jukebox-RFID/misc/sampleconfigs/startup-sound.service.stretch-default.sample /etc/systemd/system/startup-sound.service
sudo cp /home/pi/RPi-Jukebox-RFID/misc/sampleconfigs/gpio-buttons.service.stretch-default.sample /etc/systemd/system/gpio-buttons.service
sudo cp /home/pi/RPi-Jukebox-RFID/misc/sampleconfigs/idle-watchdog.service.sample /etc/systemd/system/idle-watchdog.service
sudo chown root:root /etc/systemd/system/rfid-reader.service
sudo chown root:root /etc/systemd/system/startup-sound.service
sudo chown root:root /etc/systemd/system/gpio-buttons.service
sudo chown root:root /etc/systemd/system/idle-watchdog.service
sudo chmod 644 /etc/systemd/system/rfid-reader.service
sudo chmod 644 /etc/systemd/system/startup-sound.service
sudo chmod 644 /etc/systemd/system/gpio-buttons.service
sudo chmod 644 /etc/systemd/system/idle-watchdog.service

# copy mp3s for startup and shutdown sound to the right folder
cp /home/pi/RPi-Jukebox-RFID/misc/sampleconfigs/startupsound.mp3.sample /home/pi/RPi-Jukebox-RFID/shared/startupsound.mp3
cp /home/pi/RPi-Jukebox-RFID/misc/sampleconfigs/shutdownsound.mp3.sample /home/pi/RPi-Jukebox-RFID/shared/shutdownsound.mp3

# MPD configuration
# -rw-r----- 1 mpd audio 14043 Jul 17 20:16 /etc/mpd.conf
sudo cp /home/pi/RPi-Jukebox-RFID/misc/sampleconfigs/mpd.conf.sample /etc/mpd.conf
sudo chown mpd:audio /etc/mpd.conf
sudo chmod 640 /etc/mpd.conf
# update mpc / mpd DB
mpc update

##############
# Access Point
# http://www.raspberryconnect.com/network/item/331-raspberry-pi-auto-wifi-hotspot-switch-no-internet-routing
if [ $ACCESSconfig == "YES" ]
then
    
    # Work in progress, so keep in mind: BACKUP conf files for ACCESS POINT
    # cp /etc/hostapd/hostapd.conf hostapd.conf.stretch.sample
    # cp /etc/default/hostapd hostapd.stretch.sample
    # cp /etc/dnsmasq.conf dnsmasq.conf.stretch.sample
    # cp /etc/network/interfaces interfaces.stretch.sample

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
fi

# / Access Point
################

# / INSTALLATION
##################################################### 

#####################################################
# notes for things to do

#Ask if Spotify config

#If Spotify
#Ask for user
#Ask for password

#Ask samba password
#Ask ssh password


# get existing install
# new config should be done with sed using existing conf and user input
# samba and ssh password without prompt

# CLEANUP
## remove dir BACKUP (possibly not, because we od this ta the ebginning after user confirms for latest config)
