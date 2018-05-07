#!/bin/bash
#
# see https://github.com/MiczFlor/RPi-Jukebox-RFID for details
#
# this script installs default settings from the github repo to run
# the RPi jukebox like an Access Point to connect over wifi without
# a router.
# before running the script, the RPi needs to be set up, see INSTALL-jessie.md on github
# download the install script only to home dir and run
# Don't run as sudo. Simply type ./jessie-install-AccessPoint-01.sh

# Backup Access point files like this:
#sudo cp /etc/network/interfaces /home/pi/RPi-Jukebox-RFID/misc/sampleconfigs/interfaces.jessie-WlanAP.sample
#sudo cp /etc/dhcpcd.conf /home/pi/RPi-Jukebox-RFID/misc/sampleconfigs/dhcpcd.conf.jessie-WlanAP.sample
#sudo cp /etc/dnsmasq.conf /home/pi/RPi-Jukebox-RFID/misc/sampleconfigs/dnsmasq.conf.jessie-WlanAP.sample
#sudo cp /etc/hostapd/hostapd.conf /home/pi/RPi-Jukebox-RFID/misc/sampleconfigs/hostapd.conf.jessie-WlanAP.sample
#sudo cp /etc/default/hostapd /home/pi/RPi-Jukebox-RFID/misc/sampleconfigs/hostapd.jessie-WlanAP.sample

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

# DHCP network interfaces
# -rw-r--r-- 1 root root 192 Nov 27 15:39 /etc/network/interfaces
sudo cp /home/pi/RPi-Jukebox-RFID/misc/sampleconfigs/interfaces.jessie-WlanAP.sample /etc/network/interfaces
sudo chown root:root /etc/network/interfaces
sudo chmod 644 /etc/network/interfaces

# DHCP configuration settings
# -rw-rw-r-- 1 root netdev 1371 Nov 17 21:02 /etc/dhcpcd.conf
sudo cp /home/pi/RPi-Jukebox-RFID/misc/sampleconfigs/dhcpcd.conf.jessie-WlanAP.sample /etc/dhcpcd.conf
sudo chown root:netdev /etc/dhcpcd.conf
sudo chmod 664 /etc/dhcpcd.conf

# dnsmasq configuration settings
# -rw-r--r-- 1 root root 26040 Nov 26 23:37 /etc/dnsmasq.conf
sudo cp /home/pi/RPi-Jukebox-RFID/misc/sampleconfigs/dnsmasq.conf.jessie-WlanAP.sample /etc/dnsmasq.conf
sudo chown root:root /etc/dnsmasq.conf
sudo chmod 644 /etc/dnsmasq.conf

# hostapd configuration settings
# -rw------- 1 root root 261 Nov 26 23:40 /etc/hostapd/hostapd.conf
sudo cp /home/pi/RPi-Jukebox-RFID/misc/sampleconfigs/hostapd.conf.jessie-WlanAP.sample /etc/hostapd/hostapd.conf
sudo chown root:root /etc/hostapd/hostapd.conf
sudo chmod 600 /etc/hostapd/hostapd.conf

# default hostapd settings
# rw-r--r-- 1 root root 825 Nov 26 23:45 /etc/default/hostapd
sudo cp /home/pi/RPi-Jukebox-RFID/misc/sampleconfigs/hostapd.conf.jessie-WlanAP.sample /etc/default/hostapd
sudo chown root:root /etc/default/hostapd
sudo chmod 644 /etc/default/hostapd

# Samba configuration settings
# -rw-r--r-- 1 root root 9416 Nov 17 21:04 /etc/samba/smb.conf
sudo cp /home/pi/RPi-Jukebox-RFID/misc/sampleconfigs/smb.conf.jessie-default.sample /etc/samba/smb.conf
sudo chown root:root /etc/samba/smb.conf
sudo chmod 644 /etc/samba/smb.conf

# Web server configuration settings
# -rw-r--r-- 1 root root 1063 Nov 17 21:07 /etc/lighttpd/lighttpd.conf
sudo cp /home/pi/RPi-Jukebox-RFID/misc/sampleconfigs/lighttpd.conf.jessie-default.sample /etc/lighttpd/lighttpd.conf
sudo chown root:root /etc/lighttpd/lighttpd.conf
sudo chmod 644 /etc/lighttpd/lighttpd.conf

# SUDO users (adding web server here)
# -r--r----- 1 root root 703 Nov 17 21:08 /etc/sudoers
sudo cp /home/pi/RPi-Jukebox-RFID/misc/sampleconfigs/sudoers.jessie-default.sample /etc/sudoers
sudo chown root:root /etc/sudoers
sudo chmod 440 /etc/sudoers

# crontab file for user pi
# -rw------- 1 pi crontab 1227 Nov 17 21:24 /var/spool/cron/crontabs/pi
# for debugging (which I had to on a RPi 3)  see:
# https://rahulmahale.wordpress.com/2014/09/03/solved-running-cron-job-at-reboot-on-raspberry-pi-in-debianwheezy-and-raspbian/
sudo cp /home/pi/RPi-Jukebox-RFID/misc/sampleconfigs/crontab-pi.jessie-default.sample /var/spool/cron/crontabs/pi
sudo chown pi:crontab /var/spool/cron/crontabs/pi
sudo chmod 600 /var/spool/cron/crontabs/pi

# device name for barcode reader
# Note: this will vary from reader to reader. If you run this install script, 
# read 'Register your USB device for the jukebox' in docs/CONFIGURE-jessie.md to do this step manually
# -rw-r--r-- 1 pi pi 20 Nov 17 21:22 /home/pi/RPi-Jukebox-RFID/scripts/deviceName.txt
sudo cp /home/pi/RPi-Jukebox-RFID/misc/sampleconfigs/deviceName.txt.sample /home/pi/RPi-Jukebox-RFID/scripts/deviceName.txt
sudo chown pi:pi /home/pi/RPi-Jukebox-RFID/scripts/deviceName.txt
sudo chmod 644 /home/pi/RPi-Jukebox-RFID/scripts/deviceName.txt

# copy shell script for player
# -rwxr-xr-x 1 pi pi 6253 Nov 17 21:24 /home/pi/RPi-Jukebox-RFID/scripts/rfid_trigger_play.sh
cp /home/pi/RPi-Jukebox-RFID/scripts/rfid_trigger_play.sh.sample /home/pi/RPi-Jukebox-RFID/scripts/rfid_trigger_play.sh
sudo chown pi:pi /home/pi/RPi-Jukebox-RFID/scripts/rfid_trigger_play.sh
sudo chmod 755 /home/pi/RPi-Jukebox-RFID/scripts/rfid_trigger_play.sh
# The new way of making the bash daemon is using the helperscripts 
# creating the shortcuts and script from a CSV file.
# see scripts/helperscripts/AssignIDs4Shortcuts.php

# Starting web server
sudo lighty-enable-mod fastcgi-php
sudo service lighttpd force-reload

# start DHCP
sudo service dhcpcd start
sudo systemctl enable dhcpcd

############################
# Manual intervention needed
############################

# samba user
# you must use password 'raspberry' because this is 
# expected in the smb.conf file
sudo smbpasswd -a pi



