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
# $DEBUG true|false
DEBUG=false

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
if [ $DEBUG == "true" ]
then
        echo "$NOW"   >> $PATHDATA/../logs/debug.log
fi
##################################################################
# Check if we got the card ID or the audio folder from the prompt.
# Sloppy error check, because we assume the best.
if [ "$CARDID" ]; then
    # we got the card ID
    # If you want to see the CARDID printed, uncomment the following line
    # echo CARDID = $CARDID

    # Add info into the log, making it easer to monitor cards 
    echo "Card ID '$CARDID' was used at '$NOW'." > $PATHDATA/../shared/latestID.txt
    if [ $DEBUG == "true" ]
    then
        echo "Card ID '$CARDID' was used"   >> $PATHDATA/../logs/debug.log
    fi

    # If the input is of 'special' use, don't treat it like a trigger to play audio.
    # Special uses are for example volume changes, skipping, muting sound.

    case $CARDID in 
        $CMDMUTE)
            # amixer sset 'PCM' 0%
            $PATHDATA/playout_controls.sh -c=mute
            ;;
        $CMDVOL30)
            # amixer sset 'PCM' 30%
            $PATHDATA/playout_controls.sh -c=setvolume -v=30
            ;;
        $CMDVOL50)
            # amixer sset 'PCM' 50%
            $PATHDATA/playout_controls.sh -c=setvolume -v=50
            ;;
        $CMDVOL75)
            # amixer sset 'PCM' 75%
            $PATHDATA/playout_controls.sh -c=setvolume -v=75
            ;;
        $CMDVOL85)
            # amixer sset 'PCM' 85%
            $PATHDATA/playout_controls.sh -c=setvolume -v=85
            ;;
        $CMDVOL90)
            # amixer sset 'PCM' 90%
            $PATHDATA/playout_controls.sh -c=setvolume -v=90
            ;;
        $CMDVOL95)
            # amixer sset 'PCM' 95%
            $PATHDATA/playout_controls.sh -c=setvolume -v=95
            ;;
        $CMDVOL100)
            # amixer sset 'PCM' 100%
            $PATHDATA/playout_controls.sh -c=setvolume -v=100
            ;;
        $CMDVOLUP)
            # increase volume by x% set in Audio_Volume_Change_Step
            $PATHDATA/playout_controls.sh -c=volumeup   
            ;;
        $CMDVOLDOWN)
            # decrease volume by x% set in Audio_Volume_Change_Step
            $PATHDATA/playout_controls.sh -c=volumedown
            ;;
        $CMDSTOP)
            # kill all running audio players
            $PATHDATA/playout_controls.sh -c=playerstop
            ;;
        $CMDSHUTDOWN)
            # shutdown the RPi nicely
            # sudo halt
            $PATHDATA/playout_controls.sh -c=shutdown
            ;;
        $CMDREBOOT)
            # shutdown the RPi nicely
            # sudo reboot
            $PATHDATA/playout_controls.sh -c=reboot
            ;;
        $CMDNEXT)
            # play next track in playlist (==folder)
            $PATHDATA/playout_controls.sh -c=playernext
            ;;
        $CMDPREV)
            # play previous track in playlist (==folder)
            # echo "prev" | nc.openbsd -w 1 localhost 4212
            sudo $PATHDATA/playout_controls.sh -c=playerprev
            #/usr/bin/sudo /home/pi/RPi-Jukebox-RFID/scripts/playout_controls.sh -c=playerprev
            ;;
        $CMDPAUSE)
            # pause current track
            # echo "pause" | nc.openbsd -w 1 localhost 4212
            $PATHDATA/playout_controls.sh -c=playerpause
            ;;
        $CMDPLAY)
            # play / resume current track
            # echo "play" | nc.openbsd -w 1 localhost 4212
            $PATHDATA/playout_controls.sh -c=playerplay
            ;;
        $STOPAFTER5)
            # stop player after -v minutes
            $PATHDATA/playout_controls.sh -c=playerstopafter -v=5
            ;;
        $STOPAFTER15)
            # stop player after -v minutes
            $PATHDATA/playout_controls.sh -c=playerstopafter -v=15
            ;;
        $STOPAFTER30)
            # stop player after -v minutes
            $PATHDATA/playout_controls.sh -c=playerstopafter -v=30
            ;;
        $STOPAFTER60)
            # stop player after -v minutes
            $PATHDATA/playout_controls.sh -c=playerstopafter -v=60
            ;;
        $SHUTDOWNAFTER5)
            # shutdown after -v minutes
            $PATHDATA/playout_controls.sh -c=shutdownafter -v=5
            ;;
        $SHUTDOWNAFTER15)
            # shutdown after -v minutes
            $PATHDATA/playout_controls.sh -c=shutdownafter -v=15
            ;;
        $SHUTDOWNAFTER30)
            # shutdown after -v minutes
            $PATHDATA/playout_controls.sh -c=shutdownafter -v=30
            ;;
        $SHUTDOWNAFTER60)
            # shutdown after -v minutes
            $PATHDATA/playout_controls.sh -c=shutdownafter -v=60
            ;;
        *)
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
        
            # Look for human readable shortcut in folder 'shortcuts'
            # check if CARDID has a text file by the same name - which would contain the human readable folder name
            if [ -f $PATHDATA/../shared/shortcuts/$CARDID ]
            then
                # Read human readable shortcut from file
                FOLDERNAME=`cat $PATHDATA/../shared/shortcuts/$CARDID`
                # Add info into the log, making it easer to monitor cards
                echo "This ID has been used before." >> $PATHDATA/../shared/latestID.txt
                if [ $DEBUG == "true" ]
                then
                    echo "This ID has been used before."   >> $PATHDATA/../logs/debug.log
                fi
            else
                # Human readable shortcut does not exists, so create one with the content $CARDID
                # this file can later be edited manually over the samba network
                echo "$CARDID" > $PATHDATA/../shared/shortcuts/$CARDID
                FOLDERNAME=$CARDID
                # Add info into the log, making it easer to monitor cards
                echo "This ID was used for the first time." >> $PATHDATA/../shared/latestID.txt
                if [ $DEBUG == "true" ]
                then
                    echo "This ID was used for the first time."   >> $PATHDATA/../logs/debug.log
                fi
            fi
            # Add info into the log, making it easer to monitor cards
            echo "The shortcut points to audiofolder '$FOLDERNAME'." >> $PATHDATA/../shared/latestID.txt
            if [ $DEBUG == "true" ]
            then
                echo "The shortcut points to audiofolder '$FOLDERNAME'."   >> $PATHDATA/../logs/debug.log
            fi
            ;;
    esac
fi
##############################################################
# We should now have a folder name with the audio files.
# Either from prompt of from the card ID processing above
# Sloppy error check, because we assume the best.

if mpc status | awk 'NR==2' | grep playing > /dev/null;
then 
    mpd_status="playing"
    if [ $DEBUG == "true" ]
    then
       mpc status
    fi
else 
   mpd_status="offline"
fi


if [ "$FOLDERNAME" ]; then

    # Save position (to catch playing and paused audio) for resume and clear the playlist -> audio off
    # Is has to be sudo as daemon_rfid_reader.py doesn't call this script with sudo
    # and this produces an error while saving lastplayed.dat

    sudo $PATHDATA/playout_controls.sh -c=playlistclear
    if [ $DEBUG == "true" ]
    then
         echo "Save position (to catch playing and paused audio) for resume and clear the playlist -> audio off"   >> $PATHDATA/../logs/debug.log
    fi
	
    # Before we create a new playlist, we remove the old one from the folder.
    # It's a workaround for resume playing as mpd doesn't know how its current playlist is named,
    # so we only want the current playlist in the "mpc lsplaylists" output.
    mpc lsplaylists | \
    while read i
    do
        mpc rm "$i"
    done
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
        if [ $DEBUG == "true" ]
        then
            echo "Check if we have something special to do"   >> $PATHDATA/../logs/debug.log
        fi
        case $SPECIALFORMAT in
            "podcast.txt")
                # Podcast
                PODCASTURL=`cat "$PATHDATA/../shared/audiofolders/$FOLDERNAME/podcast.txt"`
                # parse podcast XML in sloppy but efficient way and write URLs to playlist
                wget -q -O - "$PODCASTURL" | sed -n 's/.*enclosure.*url="\([^"]*\)".*/\1/p' > "$PLAYLISTPATH"
                # uncomment the following line to see playlist content in terminal
                # cat "$PLAYLISTPATH"
                if [ $DEBUG == "true" ]
                then
                    echo "Podcast: $PODCASTURL"   >> $PATHDATA/../logs/debug.log
                fi
            ;;
            "livestream.txt")
                # mpd can't read from .txt, so we have to write the livestream URL into playlist
                cat "$PATHDATA/../shared/audiofolders/$FOLDERNAME/livestream.txt" > "$PLAYLISTPATH"
                if [ $DEBUG == "true" ]
                then
                    echo "Livestream $PLAYLISTPATH"   >> $PATHDATA/../logs/debug.log
                fi
            ;;
            *)
                # Nothing special to do, folder with audio files
                # write playlist to file using the same name as the folder with ending .m3u
                # wrap $PLAYLIST string in "" to keep line breaks
        		# cd to ../shared/audiofolders as mpd accepts only filepaths relative to its music folder
        		# or starting with file:// (e.g. file:///home/pi...)
                cd $PATHDATA/../shared/audiofolders
                #find "$PATHDATA/../shared/audiofolders/$FOLDERNAME" -type f | sort -n > "$PLAYLISTPATH"
                find "$FOLDERNAME" -type f | sort -n > "$PLAYLISTPATH"
                if [ $DEBUG == "true" ]
                then
                    echo "Nothing special $PLAYLISTPATH"   >> $PATHDATA/../logs/debug.log
                fi
            ;;
        esac

        if [ $mpd_status == "playing" ]
        then
           if [ $DEBUG == "true" ]
           then 
              echo "status playing" >> $PATHDATA/../logs/debug.log
           fi
           run_folder=$(mpc lsplaylists)
           # if same playlist, only stop the player
           if [ "$FOLDERNAME" == "$run_folder" ]
           then
              if [ $DEBUG == "true" ]
              then
                 echo "Same Playlist Stop only" >> $PATHDATA/../logs/debug.log
              fi
              only_stop=1
           else
              if [ $DEBUG == "true" ]
              then
                 echo "different Playlist. Reload" >> $PATHDATA/../logs/debug.log
              fi
              # if playlist is different, stop the running player and restart with new playlist
              only_stop=0
           fi

           if [ $only_stop != 1 ]
           then
              $PATHDATA/playout_controls.sh -c=playlistaddplay -v="${FOLDERNAME}"
           fi
        else
              if [ $DEBUG == "true" ]
              then
                 echo "No Instance start with $PATHDATA/playout_controls.sh -c=playlistaddplay -v=$(echo $FOLDERNAME | rev | cut -d"/" -f1 | rev)"   >> $PATHDATA/../logs/debug.log
              fi
              # load new playlist and play
              $PATHDATA/playout_controls.sh -c=playlistaddplay -v="${FOLDERNAME}"
        fi
    else
	    if [ $DEBUG == "true" ]
            then
                echo "Path not found $PATHDATA/../shared/audiofolders/$FOLDERNAME"   >> $PATHDATA/../logs/debug.log 
            fi
    fi
fi
