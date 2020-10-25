#!/bin/bash

echo "This script will delete all config files" 
echo "including mpd.conf and the like." 
read -r -p "Do you want to proceed? [y/N] " response
case "$response" in
    [Yy][Ee][Ss]|[Yy])
        ;;
    *)
        echo "Exiting script."
        exit
        ;;
esac
echo "Proceeding and deleting."

# these ones we MUST leave
#sudo rm /etc/sudoers
#sudo rm /etc/samba/smb.conf

# these ones we will leave
#sudo rm /home/pi/RPi-Jukebox-RFID/htdocs/config.php
#sudo rm /home/pi/RPi-Jukebox-RFID/settings/rfid_trigger_play.conf

# these ones we delete
sudo rm /etc/lighttpd/lighttpd.conf
sudo rm /etc/lighttpd/conf-available/15-fastcgi-php.conf
sudo rm /etc/php/7.0/fpm/php.ini
sudo rm /home/pi/RPi-Jukebox-RFID/settings/Audio_iFace_Name
sudo rm /home/pi/RPi-Jukebox-RFID/settings/Audio_Folders_Path
sudo rm /home/pi/RPi-Jukebox-RFID/settings/Audio_Volume_Change_Step
sudo rm /home/pi/RPi-Jukebox-RFID/settings/Max_Volume_Limit
sudo rm /home/pi/RPi-Jukebox-RFID/settings/Idle_Time_Before_Shutdown
sudo rm /home/pi/RPi-Jukebox-RFID/settings/Second_Swipe
sudo rm /home/pi/RPi-Jukebox-RFID/settings/Playlists_Folders_Path
sudo rm /home/pi/RPi-Jukebox-RFID/settings/ShowCover
sudo rm /home/pi/RPi-Jukebox-RFID/scripts/gpio-buttons.py
sudo rm /etc/systemd/system/phoniebox-rfid-reader.service 
sudo rm /etc/systemd/system/phoniebox-startup-sound.service
sudo rm /etc/systemd/system/phoniebox-gpio-buttons.service
sudo rm /etc/systemd/system/phoniebox-idle-watchdog.service
sudo rm /etc/systemd/system/rfid-reader.service 
sudo rm /etc/systemd/system/startup-sound.service
sudo rm /etc/systemd/system/gpio-buttons.service
sudo rm /etc/systemd/system/idle-watchdog.service
sudo rm /etc/mpd.conf
sudo rm /etc/locale.gen
sudo rm /etc/default/locale
sudo rm /etc/mopidy/mopidy.conf
sudo rm ~/.config/mopidy/mopidy.conf
