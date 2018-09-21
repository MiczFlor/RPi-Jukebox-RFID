#!/bin/bash

# This script saves or restores the last position (song and time) in a playlist (=folder)
# Saving and restoring will only be made if a "lastplayed.dat" file is found in the folder where the 
# audio is stored.
# Usage: 
# Save the position: ./resume_play.sh -c=savepos
# Restore position and play or play from playlist position: ./resume_play-sh -c=resume -v=playlist_pos
# Enable resume for folder: ./resume_play-sh -c=enableresume -v=foldername_in_audiofolders
# Disable resume for folder: ./resume_play-sh -c=disableresume -v=foldername_in_audiofolders
#
# Call this script with "savepos" everytime
# - before you clear the playlist (mpc clear)
# - before you stop the player
# - before you shutdown the Pi (maybe not necessary as mpc stores the position between reboots, but it feels saver)

#############################################################
# $DEBUG true|false
DEBUG=false

# Set the date and time of now
NOW=`date +%Y-%m-%d.%H:%M:%S`

# path to this script
PATHDATA="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Read the args passed on by the command line
# see following file for details:
. $PATHDATA/inc.readArgsFromCommandLine.sh

# path to audio folders
AUDIOFOLDERSPATH=`cat $PATHDATA/../settings/Audio_Folders_Path`

if [ $DEBUG == "true" ]; then echo "########### SCRIPT resume_play.sh ($NOW) ##" >> $PATHDATA/../logs/debug.log; fi
if [ $DEBUG == "true" ]; then echo "VAR AUDIOFOLDERSPATH: $AUDIOFOLDERSPATH" >> $PATHDATA/../logs/debug.log; fi
if [ $DEBUG == "true" ]; then echo "VAR COMMAND: $COMMAND" >> $PATHDATA/../logs/debug.log; fi
if [ $DEBUG == "true" ]; then echo "VAR VALUE: $VALUE" >> $PATHDATA/../logs/debug.log; fi
if [ $DEBUG == "true" ]; then echo "VAR FOLDER: $FOLDER" >> $PATHDATA/../logs/debug.log; fi

# Get folder name of currently played audio 
FOLDER=`cat $PATHDATA/../settings/Latest_Folder_Played`
if [ $DEBUG == "true" ]; then echo "VAR FOLDER from settings/Latest_Folder_Played: $FOLDER" >> $PATHDATA/../logs/debug.log; fi

# Some error checking: if folder.conf does not exist, create default
if [ ! -e "$AUDIOFOLDERSPATH/$FOLDER/folder.conf" ]
then
    # now we create a default folder.conf file by calling this script
    # with the command param createDefaultFolderConf
    # (see script for details)
    # the $FOLDER would not need to be passed on, because it is already set in this script
    # see inc.writeFolderConfig.sh for details
    if [ $DEBUG == "true" ]; then echo "  - calling inc.writeFolderConfig.sh -c=createDefaultFolderConf -d=\$FOLDER" >> $PATHDATA/../logs/debug.log; fi
    . $PATHDATA/inc.writeFolderConfig.sh -c=createDefaultFolderConf -d="$FOLDER"
    if [ $DEBUG == "true" ]; then echo "  - back from inc.writeFolderConfig.sh" >> $PATHDATA/../logs/debug.log; fi
fi
# Read the current config file (include will execute == read)
. "$AUDIOFOLDERSPATH/$FOLDER/folder.conf"
if [ $DEBUG == "true" ]; then echo "  content of $AUDIOFOLDERSPATH/$FOLDER/folder.conf" >> $PATHDATA/../logs/debug.log; fi
if [ $DEBUG == "true" ]; then cat "$AUDIOFOLDERSPATH/$FOLDER/folder.conf" >> $PATHDATA/../logs/debug.log; fi

if [ $DEBUG == "true" ]; then echo "  Now doing what COMMAND wants: $COMMAND" >> $PATHDATA/../logs/debug.log; fi

case "$COMMAND" in

savepos)
    if [ $DEBUG == "true" ]; then echo "  savepos FOLDER: $FOLDER" >> $PATHDATA/../logs/debug.log; fi
    # Check if "folder.conf" exists
    if [ $RESUME == "ON" ];
    then
        # Get the elapsed time of the currently played audio file from mpd
        ELAPSED=$(echo -e "status\nclose" | nc -w 1 localhost 6600 | grep -o -P '(?<=elapsed: ).*')
        # mpd reports an elapsed time only if the audio is playing or is paused. Check if we got an elapsed time
        if [ ! -z $ELAPSED ]; # Why does -n not work here?
        then
            #Get the filename of the currently played audio
            CURRENTFILENAME=$(echo -e "currentsong\nclose" | nc -w 1 localhost 6600 | grep -o -P '(?<=file: ).*')
            # Save filename and time to folder.conf. 
            # "Stopped" for signaling -c=resume that there was a stopping event
            # (this is done to get a proper resume on the first track if the playlist has ended before)
            
            # set the vars we need to change
            CURRENTFILENAME=$CURRENTFILENAME
            ELAPSED=$ELAPSED
            PLAYSTATUS="Stopped"
            # now calling a script which will only replace these new vars in folder.conf
            # (see script for details)
            . $PATHDATA/inc.writeFolderConfig.sh
        fi
    fi
    ;;
resume)
    if [ $DEBUG == "true" ]; then echo "  entering: resume with value $RESUME" >> $PATHDATA/../logs/debug.log; fi
    # Check if RESUME is switched on
    if [ $RESUME == "ON" ];
    then
        # read vars from folder.conf
        . "$AUDIOFOLDERSPATH/$FOLDER/folder.conf"
        # will generate variables:
        #CURRENTFILENAME
        #ELAPSED
        #PLAYSTATUS
        
        # Check if we got a "savepos" command after the last "resume". Otherwise we assume that the playlist was played until the end.
        # In this case, start the playlist from beginning 
        if [ $PLAYSTATUS == "Stopped" ] 
        then
            # Get the playlist position of the file from mpd
            # Alternative approach: "mpc searchplay xx && mpc seek yy" 
            PLAYLISTPOS=$(echo -e playlistfind filename \"$CURRENTFILENAME\"\\nclose | nc -w 1 localhost 6600 | grep -o -P '(?<=Pos: ).*')

            # If the file is found, it is played from ELAPSED, otherwise start playlist from beginning. If we got a playlist position
            # play from that position, not the saved one.
            if [ ! -z $PLAYLISTPOS ] && [ -z $VALUE ] ;
            then
                echo -e seek $PLAYLISTPOS $ELAPSED \\nclose | nc -w 1 localhost 6600
            else
                echo -e "play $VALUE" | nc -w 1 localhost 6600
            fi
            # If the playlist ends without any stop/shutdown/new swipe (you've listened to all of the tracks), 
            # there's no savepos event and we would resume at the last position anywhere in the playlist. 
            # To catch these, we signal it to the next "resume" call via writing it to folder.conf that 
            # we still assume that the audio is playing. 
            # be anything here, as we won't use the information if "Playing" is found by "resume".
            
            # set the vars we need to change
            PLAYSTATUS="Playing"
            # now calling a script which will only replace these new vars in folder.conf
            # (see script for details)
            . $PATHDATA/inc.writeFolderConfig.sh
            
        else
            # We assume that the playlist ran to the end the last time and start from the beginning.
            # Or: playlist is playing and we've got a play from playlist position command.
            echo -e "play $VALUE" | nc -w 1 localhost 6600
        fi
    else
        # if no lastplayed.dat exists (resume play disabled), we play the playlist from the beginning or the given playlist position
        echo -e "play $VALUE" | nc -w 1 localhost 6600
    fi
    ;;
enableresume)
        if [ $DEBUG == "true" ]; then echo "  entering: enableresume" >> $PATHDATA/../logs/debug.log; fi
        # set the vars we need to change
        RESUME="ON"
        # now calling a script which will only replace these new vars in folder.conf
        # (see script for details)
        . $PATHDATA/inc.writeFolderConfig.sh
    ;;
disableresume)
        if [ $DEBUG == "true" ]; then echo "  entering: disableresume" >> $PATHDATA/../logs/debug.log; fi
        # set the vars we need to change
        RESUME="OFF"
        # now calling a script which will only replace these new vars in folder.conf
        # (see script for details)
        . $PATHDATA/inc.writeFolderConfig.sh
    ;;
*)
    echo "Command unknown"
    ;;
esac
