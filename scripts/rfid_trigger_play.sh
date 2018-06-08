#!/bin/bash

# Reads the card ID or the folder name with audio files
# from the command line (see Usage).
# Then attempts to get the folder name from the card ID
# or play audio folder content directly
#
# Usage for card ID
# ./rfid_trigger_play.sh -c=1234567890
# or
# ./rfid_trigger_play.sh --cardid=1234567890
#
# For folder names:
# ./rfid_trigger_play.sh -d=foldername
# or
# ./rfid_trigger_play.sh --dir=foldername

# ADD / EDIT RFID CARDS TO CONTROL THE PHONIEBOX
# All controls are assigned to RFID cards in this 
# file:
# settings/rfid_trigger_play.conf
# Please consult this file for more information.
# Do NOT edit anything in this file.

#############################################################

# The absolute path to the folder whjch contains all the scripts.
# Unless you are working with symlinks, leave the following line untouched.
PATHDATA="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# create the configuration file from sample - if it does not exist
if [ ! -f $PATHDATA/../settings/rfid_trigger_play.conf ]; then
    cp $PATHDATA/../settings/rfid_trigger_play.conf.sample $PATHDATA/../settings/rfid_trigger_play.conf
    # change the read/write so that later this might also be editable through the web app
    sudo chown -R pi:www-data $PATHDATA/../settings/rfid_trigger_play.conf
    sudo chmod -R 775 $PATHDATA/../settings/rfid_trigger_play.conf
fi

# Read configuration file
. $PATHDATA/../settings/rfid_trigger_play.conf

# Get args from command line (see Usage above)
for i in "$@"
do
case $i in
    -c=*|--cardid=*)
    CARDID="${i#*=}"
    ;;
    -d=*|--dir=*)
    FOLDERNAME="${i#*=}"
    ;;
esac
done

# Set the date and time of now
NOW=`date +%Y-%m-%d.%H:%M:%S`

##################################################################
# Check if we got the card ID or the audio folder from the prompt.
# Sloppy error check, because we assume the best.
if [ "$CARDID" ]; then
    # we got the card ID
    # If you want to see the CARDID printed, uncomment the following line
    # echo CARDID = $CARDID

    # If the input is of 'special' use, don't treat it like a trigger to play audio.
    # Special uses are for example volume changes, skipping, muting sound.

    if [ "$CARDID" == "$CMDMUTE" ]
    then
        # amixer sset 'PCM' 0%
        $PATHDATA/playout_controls.sh -c=mute
        
    elif [ "$CARDID" == "$CMDVOL30" ]
    then
        # amixer sset 'PCM' 30%
        $PATHDATA/playout_controls.sh -c=setvolume -v=30
    
    elif [ "$CARDID" == "$CMDVOL50" ]
    then
        # amixer sset 'PCM' 50%
        $PATHDATA/playout_controls.sh -c=setvolume -v=50
    
    elif [ "$CARDID" == "$CMDVOL75" ]
    then
        # amixer sset 'PCM' 75%
        $PATHDATA/playout_controls.sh -c=setvolume -v=75
    
    elif [ "$CARDID" == "$CMDVOL85" ]
    then
        # amixer sset 'PCM' 85%
        $PATHDATA/playout_controls.sh -c=setvolume -v=85
    
    elif [ "$CARDID" == "$CMDVOL90" ]
    then
        # amixer sset 'PCM' 90%
        $PATHDATA/playout_controls.sh -c=setvolume -v=90
    
    elif [ "$CARDID" == "$CMDVOL95" ]
    then
        # amixer sset 'PCM' 95%
        $PATHDATA/playout_controls.sh -c=setvolume -v=95
    
    elif [ "$CARDID" == "$CMDVOL100" ]
    then
        # amixer sset 'PCM' 100%
        $PATHDATA/playout_controls.sh -c=setvolume -v=100
    
    elif [ "$CARDID" == "$CMDVOLUP" ]
    then
        # increase volume by x% set in Audio_Volume_Change_Step
        $PATHDATA/playout_controls.sh -c=volumeup   
    
    elif [ "$CARDID" == "$CMDVOLDOWN" ]
    then
        # decrease volume by x% set in Audio_Volume_Change_Step
        $PATHDATA/playout_controls.sh -c=volumedown
    
    elif [ "$CARDID" == "$CMDSTOP" ]
    then
        # kill all running VLC media players
        # sudo pkill vlc
        $PATHDATA/playout_controls.sh -c=playerstop
    
    elif [ "$CARDID" == "$CMDSHUTDOWN" ]
    then
        # shutdown the RPi nicely
        # sudo halt
        $PATHDATA/playout_controls.sh -c=shutdown
        
    elif [ "$CARDID" == "$CMDREBOOT" ]
    then
        # shutdown the RPi nicely
        # sudo reboot
        $PATHDATA/playout_controls.sh -c=reboot
        
    elif [ "$CARDID" == "$CMDNEXT" ]
    then
        # play next track in playlist (==folder)
        # echo "next" | nc.openbsd -w 1 localhost 4212
        $PATHDATA/playout_controls.sh -c=playernext
        
    elif [ "$CARDID" == "$CMDPREV" ]
    then
        # play previous track in playlist (==folder)
        # echo "prev" | nc.openbsd -w 1 localhost 4212
        $PATHDATA/playout_controls.sh -c=playerprev
        
    elif [ "$CARDID" == "$CMDPAUSE" ]
    then
        # pause current track
        # echo "pause" | nc.openbsd -w 1 localhost 4212
        $PATHDATA/playout_controls.sh -c=playerpause
        
    elif [ "$CARDID" == "$CMDPLAY" ]
    then
        # play / resume current track
        # echo "play" | nc.openbsd -w 1 localhost 4212
        $PATHDATA/playout_controls.sh -c=playerplay
        
    elif [ "$CARDID" == "$STOPAFTER5" ]
    then
        # stop player after -v minutes
        $PATHDATA/playout_controls.sh -c=playerstopafter -v=5
        
    elif [ "$CARDID" == "$STOPAFTER15" ]
    then
        # stop player after -v minutes
        $PATHDATA/playout_controls.sh -c=playerstopafter -v=15
        
    elif [ "$CARDID" == "$STOPAFTER30" ]
    then
        # stop player after -v minutes
        $PATHDATA/playout_controls.sh -c=playerstopafter -v=30
        
    elif [ "$CARDID" == "$STOPAFTER60" ]
    then
        # stop player after -v minutes
        $PATHDATA/playout_controls.sh -c=playerstopafter -v=60
        
    elif [ "$CARDID" == "$SHUTDOWNAFTER5" ]
    then
        # shutdown after -v minutes
        $PATHDATA/playout_controls.sh -c=shutdownafter -v=5
        
    elif [ "$CARDID" == "$SHUTDOWNAFTER15" ]
    then
        # shutdown after -v minutes
        $PATHDATA/playout_controls.sh -c=shutdownafter -v=15
        
    elif [ "$CARDID" == "$SHUTDOWNAFTER30" ]
    then
        # shutdown after -v minutes
        $PATHDATA/playout_controls.sh -c=shutdownafter -v=30
        
    elif [ "$CARDID" == "$SHUTDOWNAFTER60" ]
    then
        # shutdown after -v minutes
        $PATHDATA/playout_controls.sh -c=shutdownafter -v=60
        
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
    
    fi
fi


##############################################################
# We should now have a folder name with the audio files.
# Either from prompt of from the card ID processing above
# Sloppy error check, because we assume the best.
if [ "$FOLDERNAME" ]; then
    
    # if a folder $FOLDERNAME exists, play content
    if [ -d "$PATHDATA/../shared/audiofolders/$FOLDERNAME" ]
    then
        # set path to playlist
        PLAYLISTPATH="/tmp/$FOLDERNAME.m3u"

        # Check if we have something special to do
        # Read content file names of folder into string
        SPECIALFORMAT=$(ls "$PATHDATA/../shared/audiofolders/$FOLDERNAME" | grep .txt)
        # the following switch can be extended with other 'special' formats which require
        # more complex action than just piping the folder content into a playlist
        case $SPECIALFORMAT in
            "podcast.txt")
                # Podcast
                PODCASTURL=`cat "$PATHDATA/../shared/audiofolders/$FOLDERNAME/podcast.txt"`
                # parse podcast XML in sloppy but efficient way and write URLs to playlist
                wget -q -O - "$PODCASTURL" | sed -n 's/.*enclosure.*url="\([^"]*\)" .*/\1/p' > "$PLAYLISTPATH"
                # uncomment the following line to see playlist content in terminal
                # cat "$PLAYLISTPATH"
                ;;
            *)
                # Nothing special to do, folder with audio files
                # write playlist to file using the same name as the folder with ending .m3u
                # wrap $PLAYLIST string in "" to keep line breaks
                find "$PATHDATA/../shared/audiofolders/$FOLDERNAME" -type f | sort -n > "$PLAYLISTPATH"
                ;;
        esac

        # first kill any possible running vlc process => stop playing audio
        sudo pkill vlc
    
        # now start the command line version of vlc loading the playlist
        # start as a background process (command &) - otherwise the input only works once the playlist finished
        cvlc --no-video --network-caching=10000 -I rc --rc-host localhost:4212 "$PLAYLISTPATH" &>/dev/null &

        # wait for starting vlc to give play feedback to website
        sleep 3
    fi
fi
