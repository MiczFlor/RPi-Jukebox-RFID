#!/bin/bash
# DO NOT USE UNTIL THIS LINE HAS DISAPPEARED
#
# see https://github.com/MiczFlor/RPi-Jukebox-RFID for details
#
# sketch for a luxury one line install script

clear
echo "Welcome to the install script of your:

##################################################### 
#    ___  __ ______  _  __________ ____   __  _  _  #
#   / _ \/ // / __ \/ |/ /  _/ __/(  _ \ /  \( \/ ) #
#  / ___/ _  / /_/ /    // // _/   ) _ ((  O ))  (  #
# /_/  /_//_/\____/_/|_/___/____/ (____/ \__/(_/\_) #
#                                                   #
##################################################### 

This script will install Phoniebox on your Raspberry Pi.
To do so, you must be online. The install script will 
will automatically configure:

* WiFi settings (SSID, password and static IP)

All these are optional and can also be done later
manually.

If you are ready, hit ENTER
"

read INPUT; clear

##################################################### 
#Ask if wifi config

WIFIconfig=YES

echo "###################################"
read -r -p "Do you want to configure your WiFi? [Y/n] " response
case "$response" in
    [nN][oO]|[nN])
    	WIFIconfig=NO
    	echo "You want to configure WiFi later."
    	echo "Hit ENTER to proceed to the next step."
        read INPUT; clear
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
        esac
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

#Ask if Spotify config
#Ask if access point


#If Spotify
#Ask for user
#Ask for password

#Ask samba password
#Ask ssh password

# check for existkng Phoniebox installation
# change to home directory to check relative paths
#cd
# phoniebox dir exists?
# shortcuts dir exists and not empty?
# audiofolders exists and not empty?
# card ID conf exists?
# GPIO file exists?
# Sounds startup Shutdown?
#Echo install found
#Ask if existing files and ocnfig should be used? All/None/Specify individually

# NONE delete Phoniebox dir
# ELSE 
## del dir BACKUP
## move Phoniebox dir to BACKUP

# get existing install
# new config should be done with sed using existing conf and user input
# samba nad yss password iwthout prompt

# CLEANUP
## remove dir BACKUP (possibly not, because we od this ta the ebginning after user confirms for latest config)
