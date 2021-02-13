#!/bin/bash

#sleep 1.5

####################
# play startup sound
mpgvolume=$((32768*50/100))
echo "${mpgvolume} is the mpg123 startup volume"
/usr/bin/mpg123 -f -${mpgvolume} /home/pi/RPi-Jukebox-RFID/shared/startupsound.mp3

#######################
