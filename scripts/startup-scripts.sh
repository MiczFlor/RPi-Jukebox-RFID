#!/bin/bash

# The absolute path to the folder whjch contains all the scripts.
# Unless you are working with symlinks, leave the following line untouched.
PATHDATA="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# sleep a little to make sure the boot process is complete
# sometimes the startup sound gets cut off a bit
sleep 4

###########################################################
# Read global configuration file (and create is not exists) 
# create the global configuration file from single files - if it does not exist
if [ ! -f $PATHDATA/../settings/global.conf ]; then
    . /home/pi/RPi-Jukebox-RFID/scripts/inc.writeGlobalConfig.sh
fi
. $PATHDATA/../settings/global.conf
###########################################################

####################
# play startup sound
/usr/bin/mpg123 /home/pi/RPi-Jukebox-RFID/shared/startupsound.mp3

#######################
# read out wifi config?
if [ "${READWLANIPYN}" == "ON" ]; then
    cd /home/pi/RPi-Jukebox-RFID/misc/
    /usr/bin/php /home/pi/RPi-Jukebox-RFID/scripts/helperscripts/cli_ReadWifiIp.php
fi
