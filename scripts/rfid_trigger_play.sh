#!/bin/bash

# Reads the card ID from the command line (see Usage).
# Then attempts to play all files inside a folder with
# the given ID given.
#
# Usage:
# ./rfid_trigger_play.sh -c=1234567890
# or
# ./rfid_trigger_play.sh --cardid=1234567890

# The absolute path to the folder whjch contains all the scripts.
# Unless you are working with symlinks, leave the following line untouched.
PATHDATA="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# NO CHANGES BENEATH THIS LINE
. $PATHDATA/../settings/rfid_trigger_play.conf

# Get args from command line (see Usage above)
for i in "$@"
do
case $i in
    -c=*|--cardid=*)
    CARDID="${i#*=}"
    ;;
esac
done

# If you want to see the CARDID printed, uncomment the following line
# echo CARDID = $CARDID

# Set the date and time of now
NOW=`date +%Y-%m-%d.%H:%M:%S`

# If the input is of 'special' use, don't treat it like a trigger to play audio.
# Special uses are for example volume changes, skipping, muting sound.

if [ "$CARDID" == "$CMDMUTE" ]
then
    $PATHDATA/playout_controls.sh -c=mute
    
elif [ "$CARDID" == "$CMDVOL30" ]
then
    $PATHDATA/playout_controls.sh -c=setvolume -v=30

elif [ "$CARDID" == "$CMDVOL50" ]
then
    $PATHDATA/playout_controls.sh -c=setvolume -v=50

elif [ "$CARDID" == "$CMDVOL75" ]
then
    $PATHDATA/playout_controls.sh -c=setvolume -v=75

elif [ "$CARDID" == "$CMDVOL85" ]
then
    $PATHDATA/playout_controls.sh -c=setvolume -v=85

elif [ "$CARDID" == "$CMDVOL90" ]
then
    $PATHDATA/playout_controls.sh -c=setvolume -v=90

elif [ "$CARDID" == "$CMDVOL95" ]
then
    $PATHDATA/playout_controls.sh -c=setvolume -v=95

elif [ "$CARDID" == "$CMDVOL100" ]
then
    $PATHDATA/playout_controls.sh -c=setvolume -v=100

elif [ "$CARDID" == "$CMDVOLUP" ]
then
    $PATHDATA/playout_controls.sh -c=volumeup   

elif [ "$CARDID" == "$CMDVOLDOWN" ]
then
    $PATHDATA/playout_controls.sh -c=volumedown

elif [ "$CARDID" == "$CMDQUIT" ]
then
    $PATHDATA/playout_controls.sh -c=playerquit

elif [ "$CARDID" == "$CMDSTOP" ]
then
    $PATHDATA/playout_controls.sh -c=playerstop

elif [ "$CARDID" == "$CMDSHUTDOWN" ]
then
    $PATHDATA/playout_controls.sh -c=shutdown
    
elif [ "$CARDID" == "$CMDREBOOT" ]
then
    $PATHDATA/playout_controls.sh -c=reboot
    
elif [ "$CARDID" == "$CMDNEXT" ]
then
    $PATHDATA/playout_controls.sh -c=playernext
    
elif [ "$CARDID" == "$CMDPREV" ]
then
    $PATHDATA/playout_controls.sh -c=playerprev

elif [ "$CARDID" == "$CMDTRACKREPLAY" ]
then
    $PATHDATA/playout_controls.sh -c=playerreplay

elif [ "$CARDID" == "$CMDLISTREPLAY" ]
then
    $PATHDATA/playout_controls.sh -c=restartlist
    
elif [ "$CARDID" == "$CMDPAUSE" ]
then
    $PATHDATA/playout_controls.sh -c=playerpause
    
else
    # We checked if the card was a special command, seems it wasn't.
    # Now we expect it to be a trigger for one or more audio file(s).
    # Let's look at the ID, write a bit of log information and then try to play audio.

    # Expected folder structure:
    #
    # $PATHDATA + /../shared/audiofolders/ + $FOLDERNAME
    # Note: $FOLDERNAME is read from a file inside 'shortcuts'.
    #       See manual for details
    #
    # Example:
    #
    # $PATHDATA/../shared/audiofolders/list1/01track.mp3
    #                                       /what-a-great-track.mp3
    #
    # $PATHDATA/../shared/audiofolders/list987/always-will.mp3
    #                                         /be.mp3
    #                                         /playing.mp3
    #                                         /x-alphabetically.mp3
    #
    # $PATHDATA/../shared/audiofolders/webradio/filewithURL.txt

    # Add info into the log, making it easer to monitor cards
    echo "Card ID '$CARDID' was used at '$NOW'." > $PATHDATA/../shared/latestID.txt

	# Look for human readable shortcut in folder 'shortcuts'
	# check if CARDID has a text file by the same name - which would contain the human readable folder name
	if [ -f $PATHDATA/../shared/shortcuts/$CARDID ]
	then
        # Read human readable shortcut from file
        FOLDERNAME=`cat $PATHDATA/../shared/shortcuts/$CARDID`
        # Add info into the log, making it easer to monitor cards
        echo "This ID has been used before." >> $PATHDATA/../shared/latestID.txt
	else
        # Human readable shortcut does not exists, so create one with the content $CARDID
        # this file can later be edited manually over the samba network
        echo "$CARDID" > $PATHDATA/../shared/shortcuts/$CARDID
        FOLDERNAME=$CARDID
        # Add info into the log, making it easer to monitor cards
        echo "This ID was used for the first time." >> $PATHDATA/../shared/latestID.txt
    fi
    # Add info into the log, making it easer to monitor cards
    echo "The shortcut points to audiofolder '$FOLDERNAME'." >> $PATHDATA/../shared/latestID.txt

	# if a folder $FOLDERNAME exists, play content
    if [ -d "$PATHDATA/../shared/audiofolders/$FOLDERNAME" ]
    then
        # write playlist to file using the same name as the folder with ending .m3u
        # wrap $PLAYLIST string in "" to keep line breaks
        find "$PATHDATA/../shared/audiofolders/$FOLDERNAME" -type f | sort -n > "$PATHDATA/../playlists/$FOLDERNAME.m3u"

        # first kill any possible running mpv process => stop playing audio
        sudo pkill mpv

        # now start the command line version of mpv loading the playlist
        # start as a background process (command &) - otherwise the input only works once the playlist finished
        #(mpv --no-terminal --input-ipc-server=/tmp/mpvsocket --save-position-on-quit --write-filename-in-watch-later-config "$PATHDATA/../playlists/$FOLDERNAME.m3u" &)
        (mpv --no-terminal --input-ipc-server=/tmp/mpvsocket --write-filename-in-watch-later-config "$PATHDATA/../playlists/$FOLDERNAME.m3u" &)
        
        # NOTE TO SELF: can we get rid off writing a playlist if we play the folder as we do in the index.php?
        # Currently problem with whitespaces in folder name.
        # Also, keep in mind the use of stream URLs or YouTube in text files
        # (mpv --no-video -I rc --rc-host localhost:4212 "$PATHDATA/../shared/audiofolders/$FOLDERNAME" > /dev/null 2>/dev/null &)
    fi
fi
