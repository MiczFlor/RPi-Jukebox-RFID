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

# Set the date and time of now
NOW=`date +%Y-%m-%d.%H:%M:%S`

# The absolute path to the folder whjch contains all the scripts.
# Unless you are working with symlinks, leave the following line untouched.
PATHDATA="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

#############################################################
# $DEBUG TRUE|FALSE
# Read debug logging configuration file
. $PATHDATA/../settings/debugLogging.conf

# The absolute path to the folder whjch contains all the scripts.
# Unless you are working with symlinks, leave the following line untouched.
PATHDATA="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
if [ "${DEBUG_inc_writeGlobalConfig_sh}" == "TRUE" ]; then echo "########### SCRIPT inc.writeGlobalConf.sh ($NOW) ##" >> $PATHDATA/../logs/debug.log; fi

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
# Min_Volume_Limit
# 1. create a default if file does not exist
if [ ! -f $PATHDATA/../settings/Min_Volume_Limit ]; then
    echo "1" > $PATHDATA/../settings/Min_Volume_Limit
    chmod 777 $PATHDATA/../settings/Min_Volume_Limit
fi
# 2. then|or read value from file
AUDIOVOLMINLIMIT=`cat $PATHDATA/../settings/Min_Volume_Limit`

##############################################
# Startup_Volume
# 1. create a default if file does not exist
if [ ! -f $PATHDATA/../settings/Startup_Volume ]; then
    echo "0" > $PATHDATA/../settings/Startup_Volume
    chmod 777 $PATHDATA/../settings/Startup_Volume
fi
# 2. then|or read value from file
AUDIOVOLSTARTUP=`cat $PATHDATA/../settings/Startup_Volume`

##############################################
# Change_Volume_Idle
# Change volume during idle (or only change it during Play and in the WebApp)
#TRUE=Change Volume during all Time (Default; FALSE=Change Volume only during "Play"; OnlyDown=It is possible to decrease Volume during Idle; OnlyUp=It is possible to increase Volume during Idle
# 1. create a default if file does not exist (set default do TRUE - Volume Change is possible every time)
if [ ! -f $PATHDATA/../settings/Change_Volume_Idle ]; then
    echo "TRUE" > $PATHDATA/../settings/Change_Volume_Idle
fi
# 2. then|or read value from file
VOLCHANGEIDLE=`cat $PATHDATA/../settings/Change_Volume_Idle`

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
# Mail Wlan Ip Address
# 1. create a default if file does not exist
if [ ! -f $PATHDATA/../settings/WlanIpMailAddr ]; then
    echo "" > $PATHDATA/../settings/WlanIpMailAddr
    chmod 777 $PATHDATA/../settings/WlanIpMailAddr
fi
# 2. then|or read value from file
MAILWLANIPADDR=`cat $PATHDATA/../settings/WlanIpMailAddr`

##############################################
# Mail Wlan Ip Email Address
# 1. create a default if file does not exist
if [ ! -f $PATHDATA/../settings/MailWlanIpYN ]; then
    echo "OFF" > $PATHDATA/../settings/MailWlanIpYN
    chmod 777 $PATHDATA/../settings/MailWlanIpYN
fi
# 2. then|or read value from file
MAILWLANIPYN=`cat $PATHDATA/../settings/WlanIpMailYN`

##############################################
# Read IP address of Wlan after boot?
# 1. create a default if file does not exist
if [ ! -f $PATHDATA/../settings/WlanIpReadYN ]; then
    echo "OFF" > $PATHDATA/../settings/WlanIpReadYN
    chmod 777 $PATHDATA/../settings/WlanIpReadYN
fi
# 2. then|or read value from file
READWLANIPYN=`cat $PATHDATA/../settings/WlanIpReadYN`

##############################################
# edition
# read this always, do not write default

# 1. create a default if file does not exist
#if [ ! -f $PATHDATA/../settings/edition ]; then
#    echo "classic" > $PATHDATA/../settings/edition
#    chmod 777 $PATHDATA/../settings/edition
#fi
# 2. then|or read value from file
chmod 777 $PATHDATA/../settings/edition
EDITION=`cat $PATHDATA/../settings/edition`

##############################################
# Lang
# 1. create a default if file does not exist
if [ ! -f $PATHDATA/../settings/Lang ]; then
    echo "en-UK" > $PATHDATA/../settings/Lang
    chmod 777 $PATHDATA/../settings/Lang
fi
# 2. then|or read value from file
LANG=`cat $PATHDATA/../settings/Lang`

##############################################
# version
# 1. create a default if file does not exist
if [ ! -f $PATHDATA/../settings/version ]; then
    echo "unknown" > $PATHDATA/../settings/version
    chmod 777 $PATHDATA/../settings/version
fi
# 2. then|or read value from file
VERSION=`cat $PATHDATA/../settings/version`

# AUDIOFOLDERSPATH
# PLAYLISTSFOLDERPATH
# SECONDSWIPE
# AUDIOIFACENAME
# AUDIOVOLCHANGESTEP
# AUDIOVOLMAXLIMIT
# AUDIOVOLMINLIMIT
# AUDIOVOLSTARTUP
# VOLCHANGEIDLE
# IDLETIMESHUTDOWN
# SHOWCOVER
# MAILWLANIPYN
# MAILWLANIPADDR
# READWLANIPYN
# EDITION
# LANG
# VERSION

#########################################################
# WRITE CONFIG FILE
rm "${PATHDATA}/../settings/global.conf"
echo "AUDIOFOLDERSPATH=\"${AUDIOFOLDERSPATH}\"" >> "${PATHDATA}/../settings/global.conf"
echo "PLAYLISTSFOLDERPATH=\"${PLAYLISTSFOLDERPATH}\"" >> "${PATHDATA}/../settings/global.conf"
echo "SECONDSWIPE=\"${SECONDSWIPE}\"" >> "${PATHDATA}/../settings/global.conf"
echo "AUDIOIFACENAME=\"${AUDIOIFACENAME}\"" >> "${PATHDATA}/../settings/global.conf"
echo "AUDIOVOLCHANGESTEP=\"${AUDIOVOLCHANGESTEP}\"" >> "${PATHDATA}/../settings/global.conf"
echo "AUDIOVOLMAXLIMIT=\"${AUDIOVOLMAXLIMIT}\"" >> "${PATHDATA}/../settings/global.conf"
echo "AUDIOVOLMINLIMIT=\"${AUDIOVOLMINLIMIT}\"" >> "${PATHDATA}/../settings/global.conf"
echo "AUDIOVOLSTARTUP=\"${AUDIOVOLSTARTUP}\"" >> "${PATHDATA}/../settings/global.conf"
echo "VOLCHANGEIDLE=\"${VOLCHANGEIDLE}\"" >> "${PATHDATA}/../settings/global.conf"
echo "IDLETIMESHUTDOWN=\"${IDLETIMESHUTDOWN}\"" >> "${PATHDATA}/../settings/global.conf"
echo "SHOWCOVER=\"${SHOWCOVER}\"" >> "${PATHDATA}/../settings/global.conf"
echo "READWLANIPYN=\"${READWLANIPYN}\"" >> "${PATHDATA}/../settings/global.conf"
echo "EDITION=\"${EDITION}\"" >> "${PATHDATA}/../settings/global.conf"
echo "LANG=\"${LANG}\"" >> "${PATHDATA}/../settings/global.conf"
echo "VERSION=\"${VERSION}\"" >> "${PATHDATA}/../settings/global.conf"
# Work in progress:
#echo "MAILWLANIPYN=\"${MAILWLANIPYN}\"" >> "${PATHDATA}/../settings/global.conf"
#echo "MAILWLANIPADDR=\"${MAILWLANIPADDR}\"" >> "${PATHDATA}/../settings/global.conf"

# change the read/write so that later this might also be editable through the web app
sudo chown -R pi:www-data ${PATHDATA}/../settings/global.conf
sudo chmod -R 777 ${PATHDATA}/../settings/global.conf
