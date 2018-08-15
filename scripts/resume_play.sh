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

for i in "$@"
do
case $i in
    -c=*|--command=*)
    COMMAND="${i#*=}"
    ;;
    -v=*|--value=*)
    VALUE="${i#*=}"
    ;;
    -d=*|--dir=*)
    FOLDER="${i#*=}"
    ;;
esac
done

PATHDATA="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
if [ $DEBUG == "true" ]; then echo "## SCRIPT resume_play.sh ($NOW) ##" >> $PATHDATA/../logs/debug.log; fi
if [ $DEBUG == "true" ]; then echo "VAR COMMAND: $COMMAND" >> $PATHDATA/../logs/debug.log; fi
if [ $DEBUG == "true" ]; then echo "VAR VALUE: $VALUE" >> $PATHDATA/../logs/debug.log; fi
if [ $DEBUG == "true" ]; then echo "VAR FOLDER: $FOLDER" >> $PATHDATA/../logs/debug.log; fi

# Get folder name of currently played audio by extracting the playlist name 
# ONLY if none was passed on. The "pass on" is needed to save position
# when starting a new playlist while an old is playing. In this case
# mpc lsplaylists will get confused because it has more than one.
# check if $FOLDER is empty / unset
if [ -z "$FOLDER" ]
then 
    FOLDER=$(mpc lsplaylists)
fi

case "$COMMAND" in

savepos)
    if [ $DEBUG == "true" ]; then echo "   savepos FOLDER: $FOLDER" >> $PATHDATA/../logs/debug.log; fi
    # Check if "lastplayed.dat" exists
    if [ -e "$PATHDATA/../shared/audiofolders/$FOLDER/lastplayed.dat" ];
    then
        # Get the elapsed time of the currently played audio file from mpd
        ELAPSED=$(echo -e "status\nclose" | nc -w 1 localhost 6600 | grep -o -P '(?<=elapsed: ).*')
        # mpd reports an elapsed time only if the audio is playing or is paused. Check if we got an elapsed time
        if [ ! -z $ELAPSED ]; # Why does -n not work here?
        then
            #Get the filename of the currently played audio
            CURRENTFILENAME=$(echo -e "currentsong\nclose" | nc -w 1 localhost 6600 | grep -o -P '(?<=file: ).*')
            # Save filename and time to lastplayed.dat. "Stopped" for signaling -c=resume that there was a stopping event
            # (this is done to get a proper resume on the first track if the playlist has ended before)
            # copy sample file to audiofolder
            sudo cp "$PATHDATA/../misc/lastplayed.dat.sample" "$PATHDATA/../shared/audiofolders/$FOLDER/lastplayed.dat"
            # replace values with current values
            # for $CURRENTFILENAME using | as alternate regex delimiter because of the folder path slash 
            sudo sed -i 's|%FILENAME%|'"$CURRENTFILENAME"'|' "$PATHDATA/../shared/audiofolders/$FOLDER/lastplayed.dat"
            sudo sed -i 's/%TIMESTAMP%/'"$ELAPSED"'/' "$PATHDATA/../shared/audiofolders/$FOLDER/lastplayed.dat"
            sudo sed -i 's/%PLAYSTATUS%/Stopped/' "$PATHDATA/../shared/audiofolders/$FOLDER/lastplayed.dat"
            sudo chmod 777 "$PATHDATA/../shared/audiofolders/$FOLDER/lastplayed.dat"
        fi
    fi
    ;;
resume)
    # Check if "lastplayed.dat" exists
    if [ -e "$PATHDATA/../shared/audiofolders/$FOLDER/lastplayed.dat" ];
    then
        # read vars from lastplayed.dat
        . "$PATHDATA/../shared/audiofolders/$FOLDER/lastplayed.dat"
        # will generate variables:
        #FILENAME
        #TIMESTAMP
        #PLAYSTATUS
        
        # Check if we got a "savepos" command after the last "resume". Otherwise we assume that the playlist was played until the end.
        # In this case, start the playlist from beginning 
        if [ $PLAYSTATUS == "Stopped" ] 
        then
            # Get the playlist position of the file from mpd
            # Alternative approach: "mpc searchplay xx && mpc seek yy" 
            PLAYLISTPOS=$(echo -e playlistfind filename \"$FILENAME\"\\nclose | nc -w 1 localhost 6600 | grep -o -P '(?<=Pos: ).*')

            # If the file is found, it is played from timestamp, otherwise start playlist from beginning. If we got a playlist position
            # play from that position, not the saved one.
            if [ ! -z $PLAYLISTPOS ] && [ -z $VALUE ] ;
            then
                echo -e seek $PLAYLISTPOS $TIMESTAMP \\nclose | nc -w 1 localhost 6600
            else
                echo -e "play $VALUE" | nc -w 1 localhost 6600
            fi
            # If the playlist ends without any stop/shutdown/new swipe (you've listened to all of the tracks), there's no savepos event
            # and we would resume at the last position anywhere in the playlist. To catch these, we signal it to the next "resume" call
            # via writing it to the lastplayed.dat that we still assume that the audio is playing. Remark: $FILENAME and $TIMESTAMP can
            # be anything here, as we won't use the information if "Playing" is found by "resume".
            # copy sample file to audiofolder
            sudo cp "$PATHDATA/../misc/lastplayed.dat.sample" "$PATHDATA/../shared/audiofolders/$FOLDER/lastplayed.dat"
            # replace values with current values
            # for $FILENAME using | as alternate regex delimiter because of the folder path slash 
            sudo sed -i 's|%FILENAME%|'"$FILENAME"'|' "$PATHDATA/../shared/audiofolders/$FOLDER/lastplayed.dat"
            sudo sed -i 's/%TIMESTAMP%/'"$TIMESTAMP"'/' "$PATHDATA/../shared/audiofolders/$FOLDER/lastplayed.dat"
            sudo sed -i 's/%PLAYSTATUS%/Playing/' "$PATHDATA/../shared/audiofolders/$FOLDER/lastplayed.dat"
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
    # copy sample file to audiofolder
    sudo cp "$PATHDATA/../misc/lastplayed.dat.sample" "$PATHDATA/../shared/audiofolders/$VALUE/lastplayed.dat"
    # replace values with current values
    sudo sed -i 's/%FILENAME%/filename/' "$PATHDATA/../shared/audiofolders/$VALUE/lastplayed.dat"
    sudo sed -i 's/%TIMESTAMP%/0/' "$PATHDATA/../shared/audiofolders/$VALUE/lastplayed.dat"
    sudo sed -i 's/%PLAYSTATUS%/Stopped/' "$PATHDATA/../shared/audiofolders/$VALUE/lastplayed.dat"
    sudo chmod 777 "$PATHDATA/../shared/audiofolders/$FOLDER/lastplayed.dat"
    ;;
disableresume)
    sudo rm "$PATHDATA/../shared/audiofolders/$VALUE/lastplayed.dat"
    ;;
*)
    echo "Command unknown"
    ;;
esac