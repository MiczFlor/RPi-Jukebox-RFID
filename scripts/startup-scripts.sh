#!/bin/bash

# The absolute path to the folder whjch contains all the scripts.
# Unless you are working with symlinks, leave the following line untouched.
PATHDATA="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

###########################################################
# Read global configuration file (and create is not exists) 
# create the global configuration file from single files - if it does not exist
if [ ! -f $PATHDATA/../settings/global.conf ]; then
    . /home/pi/RPi-Jukebox-RFID/scripts/inc.writeGlobalConfig.sh
fi
. $PATHDATA/../settings/global.conf
###########################################################
echo "Phoniebox is starting..."

cat $PATHDATA/../settings/version-number

cat $PATHDATA/../settings/global.conf

echo "${AUDIOVOLSTARTUP} is the mpd startup volume"

####################################
# make playists, files and folders 
# and shortcuts 
# readable and writable to all
sudo chmod -R 777 ${AUDIOFOLDERSPATH}
sudo chmod -R 777 ${PLAYLISTSFOLDERPATH}
sudo chmod -R 777 $PATHDATA/../shared/shortcuts

#########################################
# wait until mopidy/MPD server is running
STATUS=0
while [ "$STATUS" != "ACTIVE" ]; do STATUS=$(echo -e status\\nclose | nc -w 1 localhost 6600 | grep 'OK MPD'| sed 's/^.*$/ACTIVE/'); done

####################################
# check if and set volume on startup
/home/pi/RPi-Jukebox-RFID/scripts/playout_controls.sh -c=setvolumetostartup

####################
# play startup sound
mpgvolume=$((32768*${AUDIOVOLSTARTUP}/100))
echo "${mpgvolume} is the mpg123 startup volume"
/usr/bin/mpg123 -f -${mpgvolume} /home/pi/RPi-Jukebox-RFID/shared/startupsound.mp3

#######################
# re-scan music library
mpc rescan 

#######################
# read out wifi config?
if [ "${READWLANIPYN}" == "ON" ]; then
    /home/pi/RPi-Jukebox-RFID/scripts/playout_controls.sh -c=readwifiipoverspeaker
fi

#######################
# Default audio output to speakers (instead of bluetooth device) irrespective of setting at shutdown
if [ -f $PATHDATA/../settings/bluetooth-sink-switch ]; then
    BTSINKSWITCH=`cat $PATHDATA/../settings/bluetooth-sink-switch`
    if [ "${BTSINKSWITCH}" == "enabled" ]; then
	$PATHDATA/../components/bluetooth-sink-switch/bt-sink-switch.py speakers
    fi
fi



