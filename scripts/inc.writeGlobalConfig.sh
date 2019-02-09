#!/bin/bash

# Creates a global config file from all the individual
# files in the `settings` folder at:
#    settings/global.conf
# Should be called:
# 1. on startup (list startup sound) to create a latest
#    version of all settings
# 2. each settings change done in the web UI
# 3. a new feature to be implemented: manually triggered
#    in the web UI

#############################################################
# $DEBUG true|false
DEBUG=false

# Set the date and time of now
NOW=`date +%Y-%m-%d.%H:%M:%S`

# The absolute path to the folder whjch contains all the scripts.
# Unless you are working with symlinks, leave the following line untouched.
PATHDATA="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
if [ "$DEBUG" == "true" ]; then echo "########### SCRIPT conf_create_global.sh ($NOW) ##" >> $PATHDATA/../logs/debug.log; fi

# create the configuration file from sample - if it does not exist
if [ ! -f $PATHDATA/../settings/rfid_trigger_play.conf ]; then
    cp $PATHDATA/../settings/rfid_trigger_play.conf.sample $PATHDATA/../settings/rfid_trigger_play.conf
    # change the read/write so that later this might also be editable through the web app
    sudo chown -R pi:www-data $PATHDATA/../settings/rfid_trigger_play.conf
    sudo chmod -R 775 $PATHDATA/../settings/rfid_trigger_play.conf
fi

# Path to folder containing audio / streams
# 1. create a default if file does not exist
if [ ! -f $PATHDATA/../settings/Audio_Folders_Path ]; then
    echo "/home/pi/RPi-Jukebox-RFID/shared/audiofolders" > $PATHDATA/../settings/Audio_Folders_Path
    chmod 777 $PATHDATA/../settings/Audio_Folders_Path
fi
# 2. then|or read value from file
AUDIOFOLDERSPATH=`cat $PATHDATA/../settings/Audio_Folders_Path`

# Path to folder containing playlists
# 1. create a default if file does not exist
if [ ! -f $PATHDATA/../settings/Playlists_Folders_Path ]; then
    echo "/home/pi/RPi-Jukebox-RFID/playlists" > $PATHDATA/../settings/Playlists_Folders_Path
    chmod 777 $PATHDATA/../settings/Playlists_Folders_Path
fi
# 2. then|or read value from file
PLAYLISTSFOLDERPATH=`cat $PATHDATA/../settings/Playlists_Folders_Path`

##############################################
# Second swipe
# What happens when the same card is swiped a second time?
# RESTART => start the playlist again vs. PAUSE => toggle pause and play current
# 1. create a default if file does not exist
if [ ! -f $PATHDATA/../settings/Second_Swipe ]; then
    echo "RESTART" > $PATHDATA/../settings/Second_Swipe
    chmod 777 $PATHDATA/../settings/Second_Swipe
fi
# 2. then|or read value from file
SECONDSWIPE=`cat $PATHDATA/../settings/Second_Swipe`

##############################################
# Audio_iFace_Name
# 1. create a default if file does not exist
if [ ! -f $PATHDATA/../settings/Audio_iFace_Name ]; then
    echo "PCM" > $PATHDATA/../settings/Audio_iFace_Name
    chmod 777 $PATHDATA/../settings/Audio_iFace_Name
fi
# 2. then|or read value from file
AUDIOIFACENAME=`cat $PATHDATA/../settings/Audio_iFace_Name`

##############################################
# Audio_Volume_Change_Step
# 1. create a default if file does not exist
if [ ! -f $PATHDATA/../settings/Audio_Volume_Change_Step ]; then
    echo "3" > $PATHDATA/../settings/Audio_Volume_Change_Step
    chmod 777 $PATHDATA/../settings/Audio_Volume_Change_Step
fi
# 2. then|or read value from file
AUDIOVOLCHANGESTEP=`cat $PATHDATA/../settings/Audio_Volume_Change_Step`

##############################################
# Max_Volume_Limit
# 1. create a default if file does not exist
if [ ! -f $PATHDATA/../settings/Max_Volume_Limit ]; then
    echo "100" > $PATHDATA/../settings/Max_Volume_Limit
    chmod 777 $PATHDATA/../settings/Max_Volume_Limit
fi
# 2. then|or read value from file
AUDIOVOLMAXLIMIT=`cat $PATHDATA/../settings/Max_Volume_Limit`

##############################################
# Idle_Time_Before_Shutdown
# 1. create a default if file does not exist
if [ ! -f $PATHDATA/../settings/Idle_Time_Before_Shutdown ]; then
    echo "0" > $PATHDATA/../settings/Idle_Time_Before_Shutdown
    chmod 777 $PATHDATA/../settings/Idle_Time_Before_Shutdown
fi
# 2. then|or read value from file
IDLETIMESHUTDOWN=`cat $PATHDATA/../settings/Idle_Time_Before_Shutdown`

##############################################
# ShowCover
# 1. create a default if file does not exist
if [ ! -f $PATHDATA/../settings/ShowCover ]; then
    echo "ON" > $PATHDATA/../settings/ShowCover
    chmod 777 $PATHDATA/../settings/ShowCover
fi
# 2. then|or read value from file
SHOWCOVER=`cat $PATHDATA/../settings/ShowCover`

##############################################
# edition
# 1. create a default if file does not exist
if [ ! -f $PATHDATA/../settings/edition ]; then
    echo "classic" > $PATHDATA/../settings/edition
    chmod 777 $PATHDATA/../settings/edition
fi
# 2. then|or read value from file
EDITION=`cat $PATHDATA/../settings/edition`

# AUDIOFOLDERSPATH
# PLAYLISTSFOLDERPATH
# SECONDSWIPE
# AUDIOIFACENAME
# AUDIOVOLCHANGESTEP
# AUDIOVOLMAXLIMIT
# IDLETIMESHUTDOWN
# SHOWCOVER
# EDITION

#########################################################
# WRITE CONFIG FILE
rm "${PATHDATA}/../settings/global.conf"
echo "AUDIOFOLDERSPATH=\"${AUDIOFOLDERSPATH}\"" >> "${PATHDATA}/../settings/global.conf"
echo "PLAYLISTSFOLDERPATH=\"${PLAYLISTSFOLDERPATH}\"" >> "${PATHDATA}/../settings/global.conf"
echo "SECONDSWIPE=\"${SECONDSWIPE}\"" >> "${PATHDATA}/../settings/global.conf"
echo "AUDIOIFACENAME=\"${AUDIOIFACENAME}\"" >> "${PATHDATA}/../settings/global.conf"
echo "AUDIOVOLCHANGESTEP=\"${AUDIOVOLCHANGESTEP}\"" >> "${PATHDATA}/../settings/global.conf"
echo "AUDIOVOLMAXLIMIT=\"${AUDIOVOLMAXLIMIT}\"" >> "${PATHDATA}/../settings/global.conf"
echo "IDLETIMESHUTDOWN=\"${IDLETIMESHUTDOWN}\"" >> "${PATHDATA}/../settings/global.conf"
echo "SHOWCOVER=\"${SHOWCOVER}\"" >> "${PATHDATA}/../settings/global.conf"
echo "EDITION=\"${EDITION}\"" >> "${PATHDATA}/../settings/global.conf"
