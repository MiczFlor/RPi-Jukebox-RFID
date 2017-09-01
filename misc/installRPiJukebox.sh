#!/bin/bash
#
# see https://github.com/MiczFlor/RPi-Jukebox-RFID for details
#
# this script installs my personal settings on a fresh RPi install
# before running the script, the RPi needs to be set up, see INSTALL.md on github
# download the install script only to home dir and run
# Don't run as sudo. Simply type ./installRPiJukebox.sh

# NOTE TO SELF
# the IDs I use in the player shell script for special commands:
# CMDMUTE="mute"
# CMDVOL30="30"
# CMDVOL50="50"
# CMDVOL75="75"
# CMDVOL80="80"
# CMDVOL85="85"
# CMDVOL90="90"
# CMDVOL95="95"
# CMDVOL100="100"
# CMDSTOP="0007882996"
# CMDSHUTDOWN="halt"

# Install packages
sudo apt-get update
sudo apt-get install samba samba-common-bin python-dev python-pip gcc linux-headers-4.4 lighttpd php5-common php5-cgi php5 vlc mpg123 git
sudo pip install evdev

# Get github code
cd /home/pi/
git clone https://github.com/MiczFlor/RPi-Jukebox-RFID.git

# Patch VLC
sudo sed -i 's/geteuid/getppid/' /usr/bin/vlc

#####################################
# COPY CONFIG PRESETS TO LIVE FOLDERS
#####################################

# first, make all scripts 'root' user and group
sudo chown root:root /home/pi/RPi-Jukebox-RFID/misc/sampleconfigs/*

# DHCP configuration settings
sudo cp /home/pi/RPi-Jukebox-RFID/misc/sampleconfigs/dhcpcd.conf.sample /etc/dhcpcd.conf

# Samba configuration settings
sudo cp /home/pi/RPi-Jukebox-RFID/misc/sampleconfigs/smb.conf.sample /etc/samba/smb.conf

# Web server configuration settings
sudo cp /home/pi/RPi-Jukebox-RFID/misc/sampleconfigs/lighttpd.conf.sample /etc/lighttpd/lighttpd.conf

# SUDO users (adding web server here)
sudo cp /home/pi/RPi-Jukebox-RFID/misc/sampleconfigs/sudoers.sample /etc/sudoers

# crontab file for user pi
sudo cp /home/pi/RPi-Jukebox-RFID/misc/sampleconfigs/crontab-pi.sample /var/spool/cron/crontabs/pi

# device name for barcode reader
sudo cp /home/pi/RPi-Jukebox-RFID/misc/sampleconfigs/deviceName.txt.sample /home/pi/RPi-Jukebox-RFID/scripts/deviceName.txt
sudo chown pi:pi /home/pi/RPi-Jukebox-RFID/scripts/deviceName.txt

# copy shell script for player
cp /home/pi/RPi-Jukebox-RFID/scripts/rfid_trigger_play.sh.sample /home/pi/RPi-Jukebox-RFID/scripts/rfid_trigger_play.sh
# copying the script with my configs
cp /home/pi/RPi-Jukebox-RFID/misc/sampleconfigs/rfid_trigger_play.sh.sample /home/pi/RPi-Jukebox-RFID/scripts/rfid_trigger_play.sh
sudo chown pi:pi /home/pi/RPi-Jukebox-RFID/scripts/rfid_trigger_play.sh
sudo chmod +x /home/pi/RPi-Jukebox-RFID/scripts/rfid_trigger_play.sh

# Starting web server
sudo lighty-enable-mod fastcgi-php
sudo service lighttpd force-reload

# start DHCP
sudo service dhcpcd start
sudo systemctl enable dhcpcd

# creating the shortcuts for my machine
cd /home/pi/RPi-Jukebox-RFID/misc/
mkdir temp
cp shortcuts.tar temp/
cd temp
tar -xf shortcuts.tar
rm shortcuts.tar
rm placeholder
mv * ../../shared/shortcuts/

############################
# Manual intervention needed
############################

# samba user
# you must use password 'raspberry' because this is expected in the smb.conf file
sudo smbpasswd -a pi

