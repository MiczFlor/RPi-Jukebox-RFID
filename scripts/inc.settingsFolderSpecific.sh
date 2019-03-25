#!/bin/bash

# This script is called when something needs to be played
# from script: playout_controls.sh
# It then looks into the settings of the folder and changes
# settings if need be, such as single track play or shuffle

NOW=`date +%Y-%m-%d.%H:%M:%S`
if [ "$DEBUG" == "true" ]; then echo "  ######### SCRIPT inc.settingsFolderSpecific.sh ($NOW) ##" >> $PATHDATA/../logs/debug.log; fi

# Get folder name of currently played audio 
FOLDER=`cat $PATHDATA/../settings/Latest_Folder_Played`
if [ "$DEBUG" == "true" ]; then echo "  # VAR FOLDER from settings/Latest_Folder_Played: $FOLDER" >> $PATHDATA/../logs/debug.log; fi

if [ -e "$AUDIOFOLDERSPATH/$FOLDER/folder.conf" ]
then
    # Read the current config file (include will execute == read)
    . "$AUDIOFOLDERSPATH/$FOLDER/folder.conf"
    
    if [ "$DEBUG" == "true" ]; then echo "  # Folder exists: ${AUDIOFOLDERSPATH}/${FOLDER}/folder.conf" >> $PATHDATA/../logs/debug.log; fi
    if [ "$DEBUG" == "true" ]; then cat "$AUDIOFOLDERSPATH/$FOLDER/folder.conf" >> $PATHDATA/../logs/debug.log; fi
    
    # SINGLE TRACK PLAY
    if [ $SINGLE == "ON" ]
    then
        mpc single on
    else
        mpc single off
    fi
    
    # SHUFFLE FOLDER
    if [ $SHUFFLE == "ON" ]
    then 
        mpc shuffle
    else
        mpc random off
    fi
fi
