#!/bin/bash
#
# see https://github.com/MiczFlor/RPi-Jukebox-RFID for details
# Especially the docs folder for documentation

# The absolute path to the folder which contains this script
PATHDATA="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
GIT_BRANCH=${GIT_BRANCH:-master}

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
read -r INPUT

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
echo "# Phoniebox config" > "${PATHDATA}/PhonieboxInstall.conf"

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
        read -r INPUT
        # append variables to config file
        echo "WIFIconfig=$WIFIconfig" >> "${PATHDATA}/PhonieboxInstall.conf"
        # make a fallback for WiFi Country Code, because we need that even without WiFi config
        echo "WIFIcountryCode=DE" >> "${PATHDATA}/PhonieboxInstall.conf"
        ;;
    *)
        WIFIconfig=YES
        #Ask for ssid
        echo "* Type SSID name"
        read -r INPUT
        WIFIssid="$INPUT"
        #Ask for wifi country code
        echo "* WiFi Country Code (e.g. DE, GB, CZ or US)"
        read -r INPUT
        WIFIcountryCode="$INPUT"
        #Ask for password
        echo "* Type password"
        read -r INPUT
        WIFIpass="$INPUT"
        #Ask for IP
        echo "* Static IP (e.g. 192.168.1.199)"
        read -r INPUT
        WIFIip="$INPUT"
        #Ask for Router IP
        echo "* Router IP (e.g. 192.168.1.1)"
        read -r INPUT
        WIFIipRouter="$INPUT"
        echo "Your WiFi config:"
        echo "SSID      : $WIFIssid"
        echo "WiFi Country Code      : $WIFIcountryCode"
        echo "Password  : $WIFIpass"
        echo "Static IP : $WIFIip"
        echo "Router IP : $WIFIipRouter"
        read -r -p "Are these values correct? [Y/n] " response
        case "$response" in
            [nN][oO]|[nN])
                echo "The values are incorrect."
                echo "Hit ENTER to exit and start over."
                read -r INPUT; exit
                ;;
            *)
                # append variables to config file
                echo "WIFIconfig=\"$WIFIconfig\"" >> "${PATHDATA}/PhonieboxInstall.conf"
                echo "WIFIcountryCode=\"$WIFIcountryCode\"" >> "${PATHDATA}/PhonieboxInstall.conf"
                echo "WIFIssid=\"$WIFIssid\"" >> "${PATHDATA}/PhonieboxInstall.conf"
                echo "WIFIpass=\"$WIFIpass\"" >> "${PATHDATA}/PhonieboxInstall.conf"
                echo "WIFIip=\"$WIFIip\"" >> "${PATHDATA}/PhonieboxInstall.conf"
                echo "WIFIipRouter=\"$WIFIipRouter\"" >> "${PATHDATA}/PhonieboxInstall.conf"
                ;;
        esac
        ;;
esac

#####################################################
# Check for existing Phoniebox
#
# In case there is no existing install,
# set the var now for later use:
EXISTINGuse=NO

# The install will be in the home dir of user pi
# Move to home directory now to check
cd ~ || exit
if [ -d /home/pi/RPi-Jukebox-RFID ]; then
    # Houston, we found something!
    clear
echo "#####################################################
#
# . . . * alert * alert * alert * alert * . . .
#
# WARNING: an existing Phoniebox installation was found.
#
"
    # check if we find the version number
    if [ -f /home/pi/RPi-Jukebox-RFID/settings/version ]; then
        echo "The version of your installation is: $(cat RPi-Jukebox-RFID/settings/version)"
    fi
    echo "IMPORTANT: you can use the existing content and configuration files for your new install."
    echo "Whatever you chose to keep will be moved to the new install."
    echo "Everything else will remain in a folder called 'BACKUP'.
    "
    # Delete or use existing installation?
    read -r -p "Re-use config, audio and RFID codes for the new install? [Y/n] " response
    case "$response" in
        [nN][oO]|[nN])
            EXISTINGuse=NO
            echo "Phoniebox will be a fresh install. The existing version will be dropped."
            echo "Hit ENTER to proceed to the next step."
            sudo rm -rf RPi-Jukebox-RFID
            read -r INPUT
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

            # ask for things to use
            echo "Ok. You want to use stuff from the existing installation."
            echo "What would you want to keep? Answer now."
            read -r -p "RFID config for system control (e.g. 'volume up' etc.)? [Y/n] " response
            case "$response" in
                [nN][oO]|[nN])
                    EXISTINGuseRfidConf=NO
                    ;;
                *)
                    EXISTINGuseRfidConf=YES
                    ;;
            esac
            # append variables to config file
            echo "EXISTINGuseRfidConf=$EXISTINGuseRfidConf" >> "${PATHDATA}/PhonieboxInstall.conf"

            read -r -p "RFID shortcuts to play audio folders? [Y/n] " response
            case "$response" in
                [nN][oO]|[nN])
                    EXISTINGuseRfidLinks=NO
                    ;;
                *)
                    EXISTINGuseRfidLinks=YES
                    ;;
            esac
            # append variables to config file
            echo "EXISTINGuseRfidLinks=$EXISTINGuseRfidLinks" >> "${PATHDATA}/PhonieboxInstall.conf"

            read -r -p "Audio folders: use existing? [Y/n] " response
            case "$response" in
                [nN][oO]|[nN])
                    EXISTINGuseAudio=NO
                    ;;
                *)
                    EXISTINGuseAudio=YES
                    ;;
            esac
            # append variables to config file
            echo "EXISTINGuseAudio=$EXISTINGuseAudio" >> "${PATHDATA}/PhonieboxInstall.conf"

            read -r -p "GPIO: use existing file? [Y/n] " response
            case "$response" in
                [nN][oO]|[nN])
                    EXISTINGuseGpio=NO
                    ;;
                *)
                    EXISTINGuseGpio=YES
                    ;;
            esac
            # append variables to config file
            echo "EXISTINGuseGpio=$EXISTINGuseGpio" >> "${PATHDATA}/PhonieboxInstall.conf"

            read -r -p "Sound effects: use existing startup / shutdown sounds? [Y/n] " response
            case "$response" in
                [nN][oO]|[nN])
                    EXISTINGuseSounds=NO
                    ;;
                *)
                    EXISTINGuseSounds=YES
                    ;;
            esac
            # append variables to config file
            echo "EXISTINGuseSounds=$EXISTINGuseSounds" >> "${PATHDATA}/PhonieboxInstall.conf"

            echo "Thanks. Got it."
            echo "The existing install can be found in the BACKUP directory."
            echo "Hit ENTER to proceed to the next step."
            read -r INPUT
            ;;
    esac
fi
# append variables to config file
echo "EXISTINGuse=$EXISTINGuse" >> "${PATHDATA}/PhonieboxInstall.conf"

#####################################################
# Audio iFace

clear

echo "#####################################################
#
# CONFIGURE AUDIO INTERFACE (iFace)
#
# By default for the RPi the audio interface would be 'PCM'.
# But this does not work for every setup, alternatives are
# 'Master' or 'Speaker'. Other external sound cards might
# use different interface names.
# To list all available iFace names, type 'amixer scontrols'
# in the terminal.
"
read -r -p "Use PCM as iFace? [Y/n] " response
case "$response" in
    [nN][oO]|[nN])
        echo "Type the iFace name you want to use:"
        read -r INPUT
        AUDIOiFace="$INPUT"
        ;;
    *)
        AUDIOiFace="PCM"
        ;;
esac
# append variables to config file
echo "AUDIOiFace=\"$AUDIOiFace\"" >> "${PATHDATA}/PhonieboxInstall.conf"
echo "Your iFace is called'$AUDIOiFace'"
echo "Hit ENTER to proceed to the next step."
read -r INPUT

#####################################################
# Configure spotify

clear

echo "#####################################################
#
# OPTIONAL: INCLUDE SPOTIFY
#
# Note: if this is your first time installing a phoniebox
# it might be best to do a test install without Spotify
# to make sure all your hardware works.
#
# If you want to include Spotify, MUST have your
# credentials ready:
#
# * username
# * password
# * client_id
# * client_secret

"
read -r -p "Do you want to enable Spotify? [Y/n] " response
case "$response" in
    [nN][oO]|[nN])
        SPOTinstall=NO
        echo "You don't want spotify support."
        echo "Hit ENTER to proceed to the next step."
        read -r INPUT
        ;;
    *)
        SPOTinstall=YES
        clear
        echo "#####################################################
#
# CREDENTIALS for Spotify
#
# Requires Spotify username, password, client_id and client_secret
# to get connection to Spotify.
#
# (Note: You need a device with browser to generate ID and SECRET)
#
# Please go to this website:
# https://www.mopidy.com/authenticate/
# and follow the instructions.
#
# Your credential will appear on the site below the login button.
# Please note your client_id and client_secret!
#
"
        echo ""
        echo "Type your Spotify username:"
        read -r INPUT
        SPOTIuser="$INPUT"
        echo ""
        echo "Type your Spotify password:"
        read -r INPUT
        SPOTIpass="$INPUT"
        echo ""
        echo "Type your client_id:"
        read -r INPUT
        SPOTIclientid="$INPUT"
        echo ""
        echo "Type your client_secret:"
        read -r INPUT
        SPOTIclientsecret="$INPUT"
        echo ""
        echo "Hit ENTER to proceed to the next step."
        read -r INPUT
        ;;
esac
# append variables to config file
{
    echo "SPOTinstall=\"$SPOTinstall\"";
    echo "SPOTIuser=\"$SPOTIuser\"";
    echo "SPOTIpass=\"$SPOTIpass\"";
    echo "SPOTIclientid=\"$SPOTIclientid\"";
    echo "SPOTIclientsecret=\"$SPOTIclientsecret\""
} >> "${PATHDATA}/PhonieboxInstall.conf"


#####################################################
# Configure MPD

clear

echo "#####################################################
#
# CONFIGURE MPD
#
# MPD (Music Player Daemon) runs the audio output and must
# be configured. Do it now, if you are unsure.
# (Note: can be done manually later.)
"
read -r -p "Do you want to configure MPD? [Y/n] " response
case "$response" in
    [nN][oO]|[nN])
        MPDconfig=NO
        echo "You want to configure MPD later."
        echo "Hit ENTER to proceed to the next step."
        read -r INPUT
        ;;
    *)
        MPDconfig=YES
        echo "MPD will be set up with default values."
        echo "Hit ENTER to proceed to the next step."
        read -r INPUT
        ;;
esac
# append variables to config file
echo "MPDconfig=\"$MPDconfig\"" >> "${PATHDATA}/PhonieboxInstall.conf"

#####################################################
# Folder path for audio files
# default: /home/pi/RPi-Jukebox-RFID/shared/audiofolders

clear

echo "#####################################################
#
# FOLDER CONTAINING AUDIO FILES
#
# The default location for folders containing audio files:
# /home/pi/RPi-Jukebox-RFID/shared/audiofolders
#
# If unsure, keep it like this. If your files are somewhere
# else, you can specify the folder in the next step.
# IMPORTANT: the folder will not be created, only the path
# will be remembered. If you use a custom folder, you must
# create it.
"

read -r -p "Do you want to use the default location? [Y/n] " response
case "$response" in
    [nN][oO]|[nN])
        echo "Please type the absolute path here (no trailing slash)."
        echo "Default would be for example:"
        echo "/home/pi/RPi-Jukebox-RFID/shared/audiofolders"
        read -r INPUT
        DIRaudioFolders="$INPUT"
        ;;
    *)
        DIRaudioFolders="/home/pi/RPi-Jukebox-RFID/shared/audiofolders"
        ;;
esac
# append variables to config file
echo "DIRaudioFolders=\"$DIRaudioFolders\"" >> "${PATHDATA}/PhonieboxInstall.conf"
echo "Your audio folders live in this dir:"
echo $DIRaudioFolders
echo "Hit ENTER to proceed to the next step."
read -r INPUT

clear

echo "#####################################################
#
# START INSTALLATION
#
# Good news: you completed the input.
# Let the install begin.
#
# Get yourself a cup of something. The install takes
# between 15 minutes to half an hour, depending on
# your Raspberry Pi and Internet connectivity.
#
# You will be prompted later to complete the installation.
"

read -r -p "Do you want to start the installation? [Y/n] " response
case "$response" in
    [nN][oO]|[nN])
        echo "Exiting the installation."
        echo "Your configuration data was saved in this file:"
        echo "${PATHDATA}/PhonieboxInstall.conf"
        echo
        exit
        ;;
esac

#####################################################
# INSTALLATION

# Read install config as written so far
# (this might look stupid so far, but makes sense once
# the option to install from config file is introduced.)
# shellcheck source=scripts/installscripts/tests/ShellCheck/PhonieboxInstall.conf
. "${PATHDATA}/PhonieboxInstall.conf"

# power management of wifi: switch off to avoid disconnecting
sudo iwconfig wlan0 power off

# create backup of /etc/resolv.conf
sudo cp /etc/resolv.conf /etc/resolv.conf.orig

# Generate locales
sudo locale-gen "${LANG}"

# Install required packages
sudo apt-get --yes --allow-downgrades --allow-remove-essential --allow-change-held-packages install apt-transport-https
wget -q -O - https://apt.mopidy.com/mopidy.gpg | sudo apt-key add -
sudo wget -q -O /etc/apt/sources.list.d/mopidy.list https://apt.mopidy.com/buster.list

sudo apt-get update
sudo apt-get --yes upgrade
sudo apt-get install --yes libspotify-dev

# some packages are only available on raspberry pi's but not on test docker containers running on x86_64 machines
if [[ $(uname -m) =~ ^armv.+$ ]]
then
    sudo apt-get --yes --allow-downgrades --allow-remove-essential --allow-change-held-packages install raspberrypi-kernel-headers
fi

sudo apt-get --yes --allow-downgrades --allow-remove-essential --allow-change-held-packages install samba samba-common-bin gcc lighttpd php7.3-common php7.3-cgi php7.3 at mpd mpc mpg123 git ffmpeg resolvconf spi-tools

# restore backup of /etc/resolv.conf in case installation of resolvconf cleared it
sudo cp /etc/resolv.conf.orig /etc/resolv.conf

# prepare python3
sudo apt-get --yes --allow-downgrades --allow-remove-essential --allow-change-held-packages install python3 python3-dev python3-pip python3-mutagen python3-gpiozero python3-spidev

# use python3.7 as default
sudo update-alternatives --install /usr/bin/python python /usr/bin/python3.7 1

# Get github code
cd /home/pi/ || exit
git clone https://github.com/MiczFlor/RPi-Jukebox-RFID.git --branch "${GIT_BRANCH}"

# check, which branch was cloned
git --work-tree=/home/pi/RPi-Jukebox-RFID --git-dir=/home/pi/RPi-Jukebox-RFID/.git status | head -2

# Install required spotify packages
if [ $SPOTinstall == "YES" ]
then
    # keep major verson 3 of mopidy
    echo -e "Package: mopidy\nPin: version 3.*\nPin-Priority: 1001" | sudo tee /etc/apt/preferences.d/mopidy

    wget -q -O - https://apt.mopidy.com/mopidy.gpg | sudo apt-key add -
    sudo wget -q -O /etc/apt/sources.list.d/mopidy.list https://apt.mopidy.com/buster.list
    sudo apt-get update
    sudo apt-get upgrade --yes
    sudo apt-get --yes --allow-downgrades --allow-remove-essential --allow-change-held-packages install mopidy mopidy-mpd mopidy-local mopidy-spotify
    sudo apt-get --yes --allow-downgrades --allow-remove-essential --allow-change-held-packages install libspotify12 python3-cffi python3-ply python3-pycparser python3-spotify

    # Install necessary Python packages
    cd /home/pi/RPi-Jukebox-RFID/ || exit
    sudo python3 -m pip install -r requirements-spotify.txt
fi

cd /home/pi/RPi-Jukebox-RFID/misc/sampleconfigs/ || exit
sudo rm phoniebox-rfid-reader.service.stretch-default.sample
wget https://raw.githubusercontent.com/MiczFlor/RPi-Jukebox-RFID/develop/misc/sampleconfigs/phoniebox-rfid-reader.service.stretch-default.sample
cd /home/pi/RPi-Jukebox-RFID/scripts/ || exit
sudo rm RegisterDevice.py
wget https://raw.githubusercontent.com/MiczFlor/RPi-Jukebox-RFID/develop/scripts/RegisterDevice.py

# Jump into the Phoniebox dir
cd /home/pi/RPi-Jukebox-RFID || exit

# Install more required packages
sudo python3 -m pip install -r requirements.txt
sudo pip3 install -r /home/pi/RPi-Jukebox-RFID/components/rfid-reader/rfid-reader-PN532/requirements-pn532.txt

# Switch of WiFi power management
sudo iwconfig wlan0 power off

# Samba configuration settings
# -rw-r--r-- 1 root root 9416 Apr 30 09:02 /etc/samba/smb.conf
sudo cp /home/pi/RPi-Jukebox-RFID/misc/sampleconfigs/smb.conf.buster-default.sample /etc/samba/smb.conf
sudo chown root:root /etc/samba/smb.conf
sudo chmod 644 /etc/samba/smb.conf
# for $DIRaudioFolders using | as alternate regex delimiter because of the folder path slash
sudo sed -i 's|%DIRaudioFolders%|'"$DIRaudioFolders"'|' /etc/samba/smb.conf
# Samba: create user 'pi' with password 'raspberry'
(echo "raspberry"; echo "raspberry") | sudo smbpasswd -s -a pi

# Web server configuration settings
# -rw-r--r-- 1 root root 1040 Apr 30 09:19 /etc/lighttpd/lighttpd.conf
sudo cp /home/pi/RPi-Jukebox-RFID/misc/sampleconfigs/lighttpd.conf.buster-default.sample /etc/lighttpd/lighttpd.conf
sudo chown root:root /etc/lighttpd/lighttpd.conf
sudo chmod 644 /etc/lighttpd/lighttpd.conf

# Web server PHP7 fastcgi conf
# -rw-r--r-- 1 root root 398 Apr 30 09:35 /etc/lighttpd/conf-available/15-fastcgi-php.conf
sudo cp /home/pi/RPi-Jukebox-RFID/misc/sampleconfigs/15-fastcgi-php.conf.buster-default.sample /etc/lighttpd/conf-available/15-fastcgi-php.conf
sudo chown root:root /etc/lighttpd/conf-available/15-fastcgi-php.conf
sudo chmod 644 /etc/lighttpd/conf-available/15-fastcgi-php.conf
# settings for php.ini to support upload
# -rw-r--r-- 1 root root 70999 Jun 14 13:50 /etc/php/7.3/cgi/php.ini
sudo cp /home/pi/RPi-Jukebox-RFID/misc/sampleconfigs/php.ini.buster-default.sample /etc/php/7.3/cgi/php.ini
sudo chown root:root /etc/php/7.3/cgi/php.ini
sudo chmod 644 /etc/php/7.3/cgi/php.ini

# SUDO users (adding web server here)
# -r--r----- 1 root root 703 Nov 17 21:08 /etc/sudoers
sudo cp /home/pi/RPi-Jukebox-RFID/misc/sampleconfigs/sudoers.buster-default.sample /etc/sudoers
sudo chown root:root /etc/sudoers
sudo chmod 440 /etc/sudoers

# copy shell script for player
cp /home/pi/RPi-Jukebox-RFID/settings/rfid_trigger_play.conf.sample /home/pi/RPi-Jukebox-RFID/settings/rfid_trigger_play.conf

# creating files containing editable values for configuration
# DISCONTINUED: now done by MPD? echo "PCM" > /home/pi/RPi-Jukebox-RFID/settings/Audio_iFace_Name
echo "$AUDIOiFace" > /home/pi/RPi-Jukebox-RFID/settings/Audio_iFace_Name
echo "$DIRaudioFolders" > /home/pi/RPi-Jukebox-RFID/settings/Audio_Folders_Path
echo "3" > /home/pi/RPi-Jukebox-RFID/settings/Audio_Volume_Change_Step
echo "100" > /home/pi/RPi-Jukebox-RFID/settings/Max_Volume_Limit
echo "0" > /home/pi/RPi-Jukebox-RFID/settings/Idle_Time_Before_Shutdown
echo "RESTART" > /home/pi/RPi-Jukebox-RFID/settings/Second_Swipe
echo "/home/pi/RPi-Jukebox-RFID/playlists" > /home/pi/RPi-Jukebox-RFID/settings/Playlists_Folders_Path
echo "ON" > /home/pi/RPi-Jukebox-RFID/settings/ShowCover

# The new way of making the bash daemon is using the helperscripts
# creating the shortcuts and script from a CSV file.
# see scripts/helperscripts/AssignIDs4Shortcuts.php

# create config file for web app from sample
sudo cp /home/pi/RPi-Jukebox-RFID/htdocs/config.php.sample /home/pi/RPi-Jukebox-RFID/htdocs/config.php

# Starting web server and php7
sudo lighttpd-enable-mod fastcgi
sudo lighttpd-enable-mod fastcgi-php
sudo service lighttpd force-reload

# create copy of GPIO script
sudo cp /home/pi/RPi-Jukebox-RFID/misc/sampleconfigs/gpio-buttons.py.sample /home/pi/RPi-Jukebox-RFID/scripts/gpio-buttons.py
sudo chmod +x /home/pi/RPi-Jukebox-RFID/scripts/gpio-buttons.py

# make sure bash scripts have the right settings
sudo chown pi:www-data /home/pi/RPi-Jukebox-RFID/scripts/*.sh
sudo chmod +x /home/pi/RPi-Jukebox-RFID/scripts/*.sh
sudo chown pi:www-data /home/pi/RPi-Jukebox-RFID/scripts/*.py
sudo chmod +x /home/pi/RPi-Jukebox-RFID/scripts/*.py

# services to launch after boot using systemd
# -rw-r--r-- 1 root root  304 Apr 30 10:07 phoniebox-rfid-reader.service
# 1. delete old services (this is legacy, might throw errors but is necessary. Valid for versions < 1.1.8-beta)
echo "### Deleting older versions of service daemons. This might throw errors, ignore them"
sudo systemctl disable idle-watchdog
sudo systemctl disable rfid-reader
sudo systemctl disable startup-sound
sudo systemctl disable gpio-buttons
sudo rm /etc/systemd/system/rfid-reader.service
sudo rm /etc/systemd/system/startup-sound.service
sudo rm /etc/systemd/system/gpio-buttons.service
sudo rm /etc/systemd/system/idle-watchdog.service
echo "### Done with erasing old daemons. Stop ignoring errors!"
# 2. install new ones - this is version > 1.1.8-beta
sudo cp /home/pi/RPi-Jukebox-RFID/misc/sampleconfigs/phoniebox-rfid-reader.service.stretch-default.sample /etc/systemd/system/phoniebox-rfid-reader.service
sudo cp /home/pi/RPi-Jukebox-RFID/misc/sampleconfigs/phoniebox-startup-sound.service.stretch-default.sample /etc/systemd/system/phoniebox-startup-sound.service
sudo cp /home/pi/RPi-Jukebox-RFID/misc/sampleconfigs/phoniebox-gpio-buttons.service.stretch-default.sample /etc/systemd/system/phoniebox-gpio-buttons.service
sudo cp /home/pi/RPi-Jukebox-RFID/misc/sampleconfigs/phoniebox-idle-watchdog.service.sample /etc/systemd/system/phoniebox-idle-watchdog.service
sudo cp /home/pi/RPi-Jukebox-RFID/misc/sampleconfigs/phoniebox-rotary-encoder.service.stretch-default.sample /etc/systemd/system/phoniebox-rotary-encoder.service
sudo chown root:root /etc/systemd/system/phoniebox-rfid-reader.service
sudo chown root:root /etc/systemd/system/phoniebox-startup-sound.service
sudo chown root:root /etc/systemd/system/phoniebox-gpio-buttons.service
sudo chown root:root /etc/systemd/system/phoniebox-idle-watchdog.service
sudo chown root:root /etc/systemd/system/phoniebox-rotary-encoder.service
sudo chmod 644 /etc/systemd/system/phoniebox-rfid-reader.service
sudo chmod 644 /etc/systemd/system/phoniebox-startup-sound.service
sudo chmod 644 /etc/systemd/system/phoniebox-gpio-buttons.service
sudo chmod 644 /etc/systemd/system/phoniebox-idle-watchdog.service
sudo chmod 644 /etc/systemd/system/phoniebox-rotary-encoder.service
# enable the services needed
sudo systemctl enable phoniebox-idle-watchdog
sudo systemctl enable phoniebox-rfid-reader
sudo systemctl enable phoniebox-startup-sound
sudo systemctl enable phoniebox-gpio-buttons
sudo systemctl enable phoniebox-rotary-encoder.service

# copy mp3s for startup and shutdown sound to the right folder
cp /home/pi/RPi-Jukebox-RFID/misc/sampleconfigs/startupsound.mp3.sample /home/pi/RPi-Jukebox-RFID/shared/startupsound.mp3
cp /home/pi/RPi-Jukebox-RFID/misc/sampleconfigs/shutdownsound.mp3.sample /home/pi/RPi-Jukebox-RFID/shared/shutdownsound.mp3

# Spotify config
if [ $SPOTinstall == "YES" ]
then
    sudo systemctl disable mpd
    sudo systemctl enable mopidy
    # Install Config Files
    sudo cp /home/pi/RPi-Jukebox-RFID/misc/sampleconfigs/locale.gen.sample /etc/locale.gen
    sudo cp /home/pi/RPi-Jukebox-RFID/misc/sampleconfigs/locale.sample /etc/default/locale
    sudo locale-gen
    sudo mkdir /home/pi/.config
    sudo mkdir /home/pi/.config/mopidy
    sudo cp /home/pi/RPi-Jukebox-RFID/misc/sampleconfigs/mopidy-etc.sample /etc/mopidy/mopidy.conf
    sudo cp /home/pi/RPi-Jukebox-RFID/misc/sampleconfigs/mopidy.sample ~/.config/mopidy/mopidy.conf
    # Change vars to match install config
    sudo sed -i 's/%spotify_username%/'"$SPOTIuser"'/' /etc/mopidy/mopidy.conf
    sudo sed -i 's/%spotify_password%/'"$SPOTIpass"'/' /etc/mopidy/mopidy.conf
    sudo sed -i 's/%spotify_client_id%/'"$SPOTIclientid"'/' /etc/mopidy/mopidy.conf
    sudo sed -i 's/%spotify_client_secret%/'"$SPOTIclientsecret"'/' /etc/mopidy/mopidy.conf
    sudo sed -i 's/%spotify_username%/'"$SPOTIuser"'/' ~/.config/mopidy/mopidy.conf
    sudo sed -i 's/%spotify_password%/'"$SPOTIpass"'/' ~/.config/mopidy/mopidy.conf
    sudo sed -i 's/%spotify_client_id%/'"$SPOTIclientid"'/' ~/.config/mopidy/mopidy.conf
    sudo sed -i 's/%spotify_client_secret%/'"$SPOTIclientsecret"'/' ~/.config/mopidy/mopidy.conf
fi

if [ $MPDconfig == "YES" ]
then
    # MPD configuration
    # -rw-r----- 1 mpd audio 14043 Jul 17 20:16 /etc/mpd.conf
    sudo cp /home/pi/RPi-Jukebox-RFID/misc/sampleconfigs/mpd.conf.buster-default.sample /etc/mpd.conf
    # Change vars to match install config
    sudo sed -i 's/%AUDIOiFace%/'"$AUDIOiFace"'/' /etc/mpd.conf
    # for $DIRaudioFolders using | as alternate regex delimiter because of the folder path slash
    sudo sed -i 's|%DIRaudioFolders%|'"$DIRaudioFolders"'|' /etc/mpd.conf
    sudo chown mpd:audio /etc/mpd.conf
    sudo chmod 640 /etc/mpd.conf
fi

# set which version has been installed
if [ $SPOTinstall == "YES" ]
then
    echo "plusSpotify" > /home/pi/RPi-Jukebox-RFID/settings/edition
else
    echo "classic" > /home/pi/RPi-Jukebox-RFID/settings/edition
fi

# update mpc / mpd DB
mpc update

###############################
# WiFi settings (SSID password)
#
# https://www.raspberrypi.org/documentation/configuration/wireless/wireless-cli.md
#
# $WIFIssid
# $WIFIpass
# $WIFIip
# $WIFIipRouter
if [ $WIFIconfig == "YES" ]
then
    # DHCP configuration settings
    #-rw-rw-r-- 1 root netdev 0 Apr 17 11:25 /etc/dhcpcd.conf
    sudo cp /home/pi/RPi-Jukebox-RFID/misc/sampleconfigs/dhcpcd.conf.buster-default-noHotspot.sample /etc/dhcpcd.conf
    # Change IP for router and Phoniebox
    sudo sed -i 's/%WIFIip%/'"$WIFIip"'/' /etc/dhcpcd.conf
    sudo sed -i 's/%WIFIipRouter%/'"$WIFIipRouter"'/' /etc/dhcpcd.conf
    sudo sed -i 's/%WIFIcountryCode%/'"$WIFIcountryCode"'/' /etc/dhcpcd.conf
    # Change user:group and access mod
    sudo chown root:netdev /etc/dhcpcd.conf
    sudo chmod 664 /etc/dhcpcd.conf

    # WiFi SSID & Password
    # -rw-rw-r-- 1 root netdev 137 Jul 16 08:53 /etc/wpa_supplicant/wpa_supplicant.conf
    sudo cp /home/pi/RPi-Jukebox-RFID/misc/sampleconfigs/wpa_supplicant.conf.buster-default.sample /etc/wpa_supplicant/wpa_supplicant.conf
    sudo sed -i 's/%WIFIssid%/'"$WIFIssid"'/' /etc/wpa_supplicant/wpa_supplicant.conf
    sudo sed -i 's/%WIFIpass%/'"$WIFIpass"'/' /etc/wpa_supplicant/wpa_supplicant.conf
    sudo sed -i 's/%WIFIcountryCode%/'"$WIFIcountryCode"'/' /etc/wpa_supplicant/wpa_supplicant.conf
    sudo chown root:netdev /etc/wpa_supplicant/wpa_supplicant.conf
    sudo chmod 664 /etc/wpa_supplicant/wpa_supplicant.conf
fi

# start DHCP
sudo service dhcpcd start
sudo systemctl enable dhcpcd

# / WiFi settings (SSID password)
###############################

# / INSTALLATION
#####################################################

#####################################################
# EXISTING ASSETS TO USE FROM EXISTING INSTALL

if [ $EXISTINGuse == "YES" ]
then

    # RFID config for system control
    if [ $EXISTINGuseRfidConf == "YES" ]
    then
        # read old values and write them into new file (copied above already)
        # do not overwrite but use 'sed' in case there are new vars in new version installed

        # Read the existing RFID config file line by line and use
        # only lines which are separated (IFS) by '='.
        while IFS='=' read -r key val ; do
            # $var should be stripped of possible leading or trailing "
            val=${val%\"}
            val=${val#\"}
            key=${key}
            # Additional error check: key should not start with a hash and not be empty.
            if [ ! "${key:0:1}" == '#' ] && [ -n "$key" ]
            then
                # Replace the matching value in the newly created conf file
                sed -i 's/%'"$key"'%/'"$val"'/' /home/pi/RPi-Jukebox-RFID/settings/rfid_trigger_play.conf
            fi
        done </home/pi/BACKUP/settings/rfid_trigger_play.conf
    fi

    # RFID shortcuts for audio folders
    if [ $EXISTINGuseRfidLinks == "YES" ]
    then
        # copy from backup to new install
        mv /home/pi/BACKUP/shared/shortcuts/* /home/pi/RPi-Jukebox-RFID/shared/shortcuts/
    fi

    # Audio folders: use existing
    if [ $EXISTINGuseAudio == "YES" ]
    then
        # copy from backup to new install
        mv /home/pi/BACKUP/shared/audiofolders/* "$DIRaudioFolders/"
    fi

    # GPIO: use existing file
    if [ $EXISTINGuseGpio == "YES" ]
    then
        # copy from backup to new install
        mv /home/pi/BACKUP/scripts/gpio-buttons.py /home/pi/RPi-Jukebox-RFID/scripts/gpio-buttons.py
    fi

    # Sound effects: use existing startup / shutdown sounds
    if [ $EXISTINGuseSounds == "YES" ]
    then
        # copy from backup to new install
        mv /home/pi/BACKUP/shared/startupsound.mp3 /home/pi/RPi-Jukebox-RFID/shared/startupsound.mp3
        mv /home/pi/BACKUP/shared/shutdownsound.mp3 /home/pi/RPi-Jukebox-RFID/shared/shutdownsound.mp3
    fi

fi

# / EXISTING ASSETS TO USE FROM EXISTING INSTALL
#####################################################

#####################################################
# Folders and Access Settings

# create playlists folder
mkdir /home/pi/RPi-Jukebox-RFID/playlists
sudo chown -R pi:www-data /home/pi/RPi-Jukebox-RFID/playlists
sudo chmod -R 775 /home/pi/RPi-Jukebox-RFID/playlists

sudo chown -R pi:www-data /home/pi/RPi-Jukebox-RFID/playlists
sudo chmod -R 775 /home/pi/RPi-Jukebox-RFID/playlists

# make sure the shared folder is accessible by the web server
sudo chown -R pi:www-data /home/pi/RPi-Jukebox-RFID/shared
sudo chmod -R 775 /home/pi/RPi-Jukebox-RFID/shared

# make sure the htdocs folder can be changed by the web server
sudo chown -R pi:www-data /home/pi/RPi-Jukebox-RFID/htdocs
sudo chmod -R 775 /home/pi/RPi-Jukebox-RFID/htdocs

sudo chown -R pi:www-data /home/pi/RPi-Jukebox-RFID/settings
sudo chmod -R 775 /home/pi/RPi-Jukebox-RFID/settings

# audio folders might be somewhere else, so treat them separately
sudo chown pi:www-data "$DIRaudioFolders"
sudo chmod 775 "$DIRaudioFolders"

# make sure bash scripts have the right settings
sudo chown pi:www-data /home/pi/RPi-Jukebox-RFID/scripts/*.sh
sudo chmod +x /home/pi/RPi-Jukebox-RFID/scripts/*.sh
sudo chown pi:www-data /home/pi/RPi-Jukebox-RFID/scripts/*.py
sudo chmod +x /home/pi/RPi-Jukebox-RFID/scripts/*.py

# set audio volume to 100%
# see: https://github.com/MiczFlor/RPi-Jukebox-RFID/issues/54
sudo amixer cset numid=1 100%

# delete the global.conf file, in case somebody manually copied stuff back and forth
# this will be created the first time the Phoniebox is put to use
# by web app or RFID
GLOBAL_CONF=/home/pi/RPi-Jukebox-RFID/settings/global.conf
if [ -f $GLOBAL_CONF ]
then
   echo "global.conf needs to be deleted."
   rm $GLOBAL_CONF
fi

# / Access settings
#####################################################

echo "
#
# INSTALLATION FINISHED
#
#####################################################
"

#####################################################
# Register external device(s)

echo "If you are using an USB RFID reader, connect it to your RPi."
echo "(In case your RFID reader required soldering, consult the manual.)"
read -r -p "Have you connected your USB Reader? [Y/n] " response
case "$response" in
    [nN][oO]|[nN])
        ;;
    *)
        cd /home/pi/RPi-Jukebox-RFID/scripts/ || exit
        python3 RegisterDevice.py
        sudo chown pi:www-data /home/pi/RPi-Jukebox-RFID/scripts/deviceName.txt
        sudo chmod 644 /home/pi/RPi-Jukebox-RFID/scripts/deviceName.txt
        ;;
esac

echo
echo "DONE. Let the sounds begin."
echo "Find more information and documentation on the github account:"
echo "https://github.com/MiczFlor/RPi-Jukebox-RFID/wiki/"

echo "Reboot is needed to activate all settings"
read -r -p "Would you like to reboot now? [Y/n] " response
case "$response" in
    [nN][oO]|[nN])
        ;;
    *)
        sudo shutdown -r now
        ;;
esac

#####################################################
# notes for things to do

# Soundcard
# PCM is currently set
# This needs to be done for mpd and in settings folder

#Ask ssh password

# get existing install
# new config should be done with sed using existing conf and user input

# CLEANUP
## remove dir BACKUP (possibly not, because we do this at the beginning after user confirms for latest config)
