#!/bin/bash

# Check all conf files copied and modified after installation script

echo "************************************"
echo "*** PHONIEBOX INFO"
echo "*** version:" $(cat /home/pi/RPi-Jukebox-RFID/settings/version)
echo "*** edition:" $(cat /home/pi/RPi-Jukebox-RFID/settings/edition)
echo "*** Audio_iFace_Name:" $(cat /home/pi/RPi-Jukebox-RFID/settings/Audio_iFace_Name)
echo "*** Audio_Folders_Path:" $(cat /home/pi/RPi-Jukebox-RFID/settings/Audio_Folders_Path)
echo "*** Audio_Volume_Change_Step:" $(cat /home/pi/RPi-Jukebox-RFID/settings/Audio_Volume_Change_Step)
echo "*** Max_Volume_Limit:" $(cat /home/pi/RPi-Jukebox-RFID/settings/Max_Volume_Limit)
echo "*** Idle_Time_Before_Shutdown:" $(cat /home/pi/RPi-Jukebox-RFID/settings/Idle_Time_Before_Shutdown)
echo "*** Second_Swipe:" $(cat /home/pi/RPi-Jukebox-RFID/settings/Second_Swipe)
echo "*** Playlists_Folders_Path:" $(cat /home/pi/RPi-Jukebox-RFID/settings/Playlists_Folders_Path)
echo "*** ShowCover:" $(cat /home/pi/RPi-Jukebox-RFID/settings/ShowCover)

echo "************************************"
echo "*** CONF FILES DEFAULT"
echo " "

echo "*** /etc/samba/smb.conf"
ls -lh /etc/samba/smb.conf
sudo cat /etc/samba/smb.conf | grep path=

echo "*** /etc/lighttpd/lighttpd.conf"
ls -lh /etc/lighttpd/lighttpd.conf

echo "*** /etc/lighttpd/conf-available/15-fastcgi-php.conf"
ls -lh /etc/lighttpd/conf-available/15-fastcgi-php.conf

echo "*** /etc/php/7.0/fpm/php.ini"
ls -lh /etc/php/7.0/fpm/php.ini

echo "*** /etc/sudoers"
ls -lh /etc/sudoers

echo "*** /etc/systemd/system/phoniebox*"
ls -lh /etc/systemd/system/phoniebox-rfid-reader.service
ls -lh /etc/systemd/system/phoniebox-startup-sound.service
ls -lh /etc/systemd/system/phoniebox-gpio-buttons.service
ls -lh /etc/systemd/system/phoniebox-idle-watchdog.service

echo "*** /etc/mpd.conf"
ls -lh /etc/mpd.conf
sudo cat /etc/mpd.conf | grep music_directory
sudo cat /etc/mpd.conf | grep mixer_control

echo "*** /etc/dhcpcd.conf"
ls -lh /etc/dhcpcd.conf
sudo cat /etc/dhcpcd.conf | grep ip_address
sudo cat /etc/dhcpcd.conf | grep routers
sudo cat /etc/dhcpcd.conf | grep domain_name_servers

echo "*** /etc/wpa_supplicant/wpa_supplicant.conf"
ls -lh /etc/wpa_supplicant/wpa_supplicant.conf
sudo cat /etc/wpa_supplicant/wpa_supplicant.conf | grep country=
#sudo cat /etc/wpa_supplicant/wpa_supplicant.conf | grep ssid=
#sudo cat /etc/wpa_supplicant/wpa_supplicant.conf | grep psk=

echo "************************************"
echo "*** +Spotify Edition"
echo " "

echo "*** /etc/locale.gen"
ls -lh /etc/locale.gen

echo "*** /etc/locale.gen"
ls -lh /etc/locale.gen

echo "*** /etc/mopidy/mopidy.conf"
ls -lh /etc/mopidy/mopidy.conf
sudo cat /etc/mopidy/mopidy.conf | grep username
#sudo cat /etc/mopidy/mopidy.conf | grep password
#sudo cat /etc/mopidy/mopidy.conf | grep client_id
#sudo cat /etc/mopidy/mopidy.conf | grep client_secret 

echo "*** ~/.config/mopidy/mopidy.conf"
ls -lh ~/.config/mopidy/mopidy.conf
sudo cat ~/.config/mopidy/mopidy.conf | grep username
#sudo cat ~/.config/mopidy/mopidy.conf | grep password
#sudo cat ~/.config/mopidy/mopidy.conf | grep client_id
#sudo cat ~/.config/mopidy/mopidy.conf | grep client_secret

echo " "
