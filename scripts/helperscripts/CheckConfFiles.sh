#!/bin/bash

# Check all conf files copied and modified after installation script

echo "### /etc/samba/smb.conf"
ls -lh /etc/samba/smb.conf
sudo cat /etc/samba/smb.conf | grep path=

echo "### /etc/lighttpd/lighttpd.conf"
ls -lh /etc/lighttpd/lighttpd.conf

echo "### /etc/lighttpd/conf-available/15-fastcgi-php.conf"
ls -lh /etc/lighttpd/conf-available/15-fastcgi-php.conf

echo "### /etc/php/7.0/fpm/php.ini"
ls -lh /etc/php/7.0/fpm/php.ini

echo "### /etc/sudoers"
ls -lh /etc/sudoers

echo "### /etc/systemd/system/phoniebox*"
ls -lh /etc/systemd/system/phoniebox-rfid-reader.service
ls -lh /etc/systemd/system/phoniebox-startup-sound.service
ls -lh /etc/systemd/system/phoniebox-gpio-buttons.service
ls -lh /etc/systemd/system/phoniebox-idle-watchdog.service

echo "### /etc/mpd.conf"
ls -lh /etc/mpd.conf
sudo cat /etc/mpd.conf | grep music_directory
sudo cat /etc/mpd.conf | grep mixer_control

echo "### /etc/dhcpcd.conf"
ls -lh /etc/dhcpcd.conf
sudo cat /etc/dhcpcd.conf
echo " "

echo "### /etc/wpa_supplicant/wpa_supplicant.conf"
ls -lh /etc/wpa_supplicant/wpa_supplicant.conf
sudo cat /etc/wpa_supplicant/wpa_supplicant.conf
echo " "

echo "####################################"
echo "### +Spotify Edition"
echo " "

echo "### /etc/locale.gen"
ls -lh /etc/locale.gen

echo "### /etc/locale.gen"
ls -lh /etc/locale.gen

echo "### /etc/mopidy/mopidy.conf"
ls -lh /etc/mopidy/mopidy.conf
sudo cat /etc/mopidy/mopidy.conf | grep username
sudo cat /etc/mopidy/mopidy.conf | grep password
sudo cat /etc/mopidy/mopidy.conf | grep client_id
sudo cat /etc/mopidy/mopidy.conf | grep client_secret 

echo "### ~/.config/mopidy/mopidy.conf"
ls -lh ~/.config/mopidy/mopidy.conf
sudo cat ~/.config/mopidy/mopidy.conf | grep username
sudo cat ~/.config/mopidy/mopidy.conf | grep password
sudo cat ~/.config/mopidy/mopidy.conf | grep client_id
sudo cat ~/.config/mopidy/mopidy.conf | grep client_secret

echo " "
