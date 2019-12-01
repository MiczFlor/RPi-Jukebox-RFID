#!/bin/bash

# This script saves or restores the SHUFFLE status in a playlist (=folder) and enables/disables shuffle mode according to the folder.conf of the current folder/playlist
# Usage: 
# Enable shuffle for folder: ./shuffle_play-sh -c=enableshuffle -v=foldername_in_audiofolders
# Disable resume for folder: ./shuffle_play-sh -c=disableshuffle -v=foldername_in_audiofolders
#
# TODO: When to call this script?
# Call this script with "playlistaddplay" (playout_controls.sh) everytime

# Set the date and time of now
NOW=`date +%Y-%m-%d.%H:%M:%S`

# The absolute path to the folder whjch contains all the scripts.
# Unless you are working with symlinks, leave the following line untouched.
PATHDATA="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

#############################################################
# $DEBUG TRUE|FALSE
# Read debug logging configuration file
. $PATHDATA/../settings/debugLogging.conf

# Read the args passed on by the command line
# see following file for details:
. $PATHDATA/inc.readArgsFromCommandLine.sh

# path to audio folders
AUDIOFOLDERSPATH=`cat $PATHDATA/../settings/Audio_Folders_Path`

if [ "${DEBUG_shuffle_play_sh}" == "TRUE" ]; then echo "## SCRIPT shuffle_play.sh ($NOW) ##" >> $PATHDATA/../logs/debug.log; fi
if [ "${DEBUG_shuffle_play_sh}" == "TRUE" ]; then echo "VAR AUDIOFOLDERSPATH: $AUDIOFOLDERSPATH" >> $PATHDATA/../logs/debug.log; fi
if [ "${DEBUG_shuffle_play_sh}" == "TRUE" ]; then echo "VAR COMMAND: $COMMAND" >> $PATHDATA/../logs/debug.log; fi
if [ "${DEBUG_shuffle_play_sh}" == "TRUE" ]; then echo "VAR VALUE: $VALUE" >> $PATHDATA/../logs/debug.log; fi
if [ "${DEBUG_shuffle_play_sh}" == "TRUE" ]; then echo "VAR FOLDER: $FOLDER" >> $PATHDATA/../logs/debug.log; fi

# Get folder name of currently played audio by extracting the playlist name 
# ONLY if none was passed on. The "pass on" is needed to save position
# when starting a new playlist while an old is playing. In this case
# mpc lsplaylists will get confused because it has more than one.
# check if $FOLDER is empty / unset
if [ -z "$FOLDER" ]
then 
    # this is old: FOLDER=$(mpc lsplaylists)
    # actually, this should be the latest folder:
    FOLDER=$(cat $PATHDATA/../settings/Latest_Folder_Played)
fi

# Some error checking: if folder.conf does not exist, create default
if [ ! -e "$AUDIOFOLDERSPATH/$FOLDER/folder.conf" ]
then
    # now we create a default folder.conf file by calling this script
    # with the command param createDefaultFolderConf
    # (see script for details)
    # the $FOLDER would not need to be passed on, because it is already set in this script
    # see inc.writeFolderConfig.sh for details
    if [ "${DEBUG_shuffle_play_sh}" == "TRUE" ]; then echo "  - calling inc.writeFolderConfig.sh -c=createDefaultFolderConf -d=\$FOLDER" >> $PATHDATA/../logs/debug.log; fi
    . $PATHDATA/inc.writeFolderConfig.sh -c=createDefaultFolderConf -d="$FOLDER"
    if [ "${DEBUG_shuffle_play_sh}" == "TRUE" ]; then echo "  - back from inc.writeFolderConfig.sh" >> $PATHDATA/../logs/debug.log; fi
fi
# Read the current config file (include will execute == read)
. "$AUDIOFOLDERSPATH/$FOLDER/folder.conf"
if [ "${DEBUG_shuffle_play_sh}" == "TRUE" ]; then echo "# found content in folder.conf:" >> $PATHDATA/../logs/debug.log; fi
if [ "${DEBUG_shuffle_play_sh}" == "TRUE" ]; then cat "$AUDIOFOLDERSPATH/$FOLDER/folder.conf" >> $PATHDATA/../logs/debug.log; fi

if [ "${DEBUG_shuffle_play_sh}" == "TRUE" ]; then echo "  Now doing what COMMAND wants: $COMMAND" >> $PATHDATA/../logs/debug.log; fi

case "$COMMAND" in

shuffle_check)
    #Check if SHUFFLE is switched on. As this is called for each playlist change, it will overwrite temporary shuffle mode
	if [ $SHUFFLE == "ON" ];
	then 
		if [ "${DEBUG_shuffle_play_sh}" == "TRUE" ]; then echo "  entering: shuffle_check with value $SHUFFLE" >> $PATHDATA/../logs/debug.log; fi
		mpc shuffle
	else
		if [ "${DEBUG_shuffle_play_sh}" == "TRUE" ]; then echo "  entering: shuffle_check with value $SHUFFLE" >> $PATHDATA/../logs/debug.log; fi
		mpc random off
	fi
    ;;
enableshuffle)
        if [ "${DEBUG_shuffle_play_sh}" == "TRUE" ]; then echo "  entering: enableshuffle" >> $PATHDATA/../logs/debug.log; fi
        # set the vars we need to change
        SHUFFLE="ON"
        # now calling a script which will only replace these new vars in folder.conf
        # (see script for details)
        . $PATHDATA/inc.writeFolderConfig.sh
    ;;
disableshuffle)
        if [ "${DEBUG_shuffle_play_sh}" == "TRUE" ]; then echo "  entering: disableshuffle" >> $PATHDATA/../logs/debug.log; fi
        # set the vars we need to change
        SHUFFLE="OFF"
        # now calling a script which will only replace these new vars in folder.conf
        # (see script for details)
        . $PATHDATA/inc.writeFolderConfig.sh
    ;;


*)
    echo "Command unknown"
    ;;
esac

if [ "${DEBUG_shuffle_play_sh}" == "TRUE" ]; then echo "# new content in folder.conf:" >> $PATHDATA/../logs/debug.log; fi
if [ "${DEBUG_shuffle_play_sh}" == "TRUE" ]; then cat "$AUDIOFOLDERSPATH/$FOLDER/folder.conf" >> $PATHDATA/../logs/debug.log; fi
