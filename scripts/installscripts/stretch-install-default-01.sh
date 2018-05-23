#!/bin/bash
#
# see https://github.com/MiczFlor/RPi-Jukebox-RFID for details
#
# this script installs my personal settings on a fresh RPi install
# before running the script, the RPi needs to be set up, see INSTALL-stretch.md on github
# download the install script only to home dir and run
# Don't run as sudo. Simply type ./stretch-install-default-01.sh

# If you want to make this work with your wifi network, change the following files before you run this script:
# dhcpcd.conf.jessie-default.sample

# Install packages
sudo apt-get update
sudo apt-get install apt-transport-https samba samba-common-bin python-dev python-pip gcc linux-headers-4.9 lighttpd php7.0-common php7.0-cgi php7.0 php7.0-fpm vlc mpg123 git
sudo pip install "evdev == 0.7.0"

# Get github code
cd /home/pi/
git clone https://github.com/MiczFlor/RPi-Jukebox-RFID.git

# Patch VLC
sudo sed -i 's/geteuid/getppid/' /usr/bin/vlc

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
cp /home/pi/RPi-Jukebox-RFID/scripts/rfid_trigger_play.sh.sample /home/pi/RPi-Jukebox-RFID/scripts/rfid_trigger_play.sh
sudo chown pi:pi /home/pi/RPi-Jukebox-RFID/scripts/rfid_trigger_play.sh
sudo chmod 775 /home/pi/RPi-Jukebox-RFID/scripts/rfid_trigger_play.sh

# copy bash script for player controls
cp /home/pi/RPi-Jukebox-RFID/scripts/playout_controls.sh.sample /home/pi/RPi-Jukebox-RFID/scripts/playout_controls.sh
sudo chown pi:pi /home/pi/RPi-Jukebox-RFID/scripts/playout_controls.sh
sudo chmod 775 /home/pi/RPi-Jukebox-RFID/scripts/playout_controls.sh

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
sudo chown root:root /etc/systemd/system/rfid-reader.service
sudo chown root:root /etc/systemd/system/startup-sound.service
sudo chown root:root /etc/systemd/system/gpio-buttons.service
sudo chmod 644 /etc/systemd/system/rfid-reader.service
sudo chmod 644 /etc/systemd/system/startup-sound.service
sudo chmod 644 /etc/systemd/system/gpio-buttons.service

############################
# Manual intervention needed
############################

# samba user
# you must use password 'raspberry' because this is 
# expected in the smb.conf file
sudo smbpasswd -a pi

