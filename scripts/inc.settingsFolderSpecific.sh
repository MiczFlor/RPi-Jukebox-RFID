#!/bin/bash

# This script is called when something needs to be played
# from script: playout_controls.sh
# It then looks into the settings of the folder and changes
# settings if need be, such as single track play or shuffle

NOW=`date +%Y-%m-%d.%H:%M:%S`

# The absolute path to the folder whjch contains all the scripts.
# Unless you are working with symlinks, leave the following line untouched.
PATHDATA="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

#############################################################
# $DEBUG TRUE|FALSE
# Read debug logging configuration file
. $PATHDATA/../settings/debugLogging.conf

if [ "${DEBUG_inc_settingsFolderSpecific_sh}" == "TRUE" ]; then echo "  #START### SCRIPT inc.settingsFolderSpecific.sh ($NOW) ##" >> $PATHDATA/../logs/debug.log; fi

# Get folder name of currently played audio 
if [ "x${FOLDER}" == "x" ]
then
  FOLDER=$(cat $PATHDATA/../settings/Latest_Folder_Played)

  if [ "${DEBUG_inc_settingsFolderSpecific_sh}" == "TRUE" ]; then echo "  # VAR FOLDER from settings/Latest_Folder_Played: $FOLDER" >> $PATHDATA/../logs/debug.log; fi
fi

if [ -e "$AUDIOFOLDERSPATH/$FOLDER/folder.conf" ]
then
    # Read the current config file (include will execute == read)
    . "$AUDIOFOLDERSPATH/$FOLDER/folder.conf"
    
    if [ "${DEBUG_inc_settingsFolderSpecific_sh}" == "TRUE" ]; then echo "  # Folder exists: ${AUDIOFOLDERSPATH}/${FOLDER}/folder.conf" >> $PATHDATA/../logs/debug.log; fi
    if [ "${DEBUG_inc_settingsFolderSpecific_sh}" == "TRUE" ]; then cat "$AUDIOFOLDERSPATH/$FOLDER/folder.conf" >> $PATHDATA/../logs/debug.log; fi
    
    # SINGLE TRACK PLAY (== shuffle can not be on, because single on will play one track after another)
    if [ "${DEBUG_inc_settingsFolderSpecific_sh}" == "TRUE" ]; then echo "  # SINGLE TRACK PLAY: $SINGLE" >> $PATHDATA/../logs/debug.log; fi
    if [ $SINGLE == "ON" ]
    then
		if [ "${DEBUG_inc_settingsFolderSpecific_sh}" == "TRUE" ]; then echo "  # # CHANGING: mpc single on" >> $PATHDATA/../logs/debug.log; fi
        mpc single on
        mpc random off
    else
		if [ "${DEBUG_inc_settingsFolderSpecific_sh}" == "TRUE" ]; then echo "  # # CHANGING: mpc single off" >> $PATHDATA/../logs/debug.log; fi
        mpc single off
        # only now we might shuffle
        # SHUFFLE FOLDER
        if [ "${DEBUG_inc_settingsFolderSpecific_sh}" == "TRUE" ]; then echo "  # SHUFFLE FOLDER: $SHUFFLE" >> $PATHDATA/../logs/debug.log; fi
        if [ $SHUFFLE == "ON" ]
        then 
		    if [ "${DEBUG_inc_settingsFolderSpecific_sh}" == "TRUE" ]; then echo "  # # CHANGING: mpc shuffle" >> $PATHDATA/../logs/debug.log; fi
            # mpc shuffle
        else
		    if [ "${DEBUG_inc_settingsFolderSpecific_sh}" == "TRUE" ]; then echo "  # # CHANGING: mpc random off" >> $PATHDATA/../logs/debug.log; fi
            mpc random off
        fi
    fi
    
fi

if [ "${DEBUG_inc_settingsFolderSpecific_sh}" == "TRUE" ]; then echo "  #END##### SCRIPT inc.settingsFolderSpecific.sh ($NOW) ##" >> $PATHDATA/../logs/debug.log; fi
