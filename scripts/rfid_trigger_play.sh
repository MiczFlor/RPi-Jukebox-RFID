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

# Set the date and time of now
NOW=`date +%Y-%m-%d.%H:%M:%S`

# The absolute path to the folder whjch contains all the scripts.
# Unless you are working with symlinks, leave the following line untouched.
PATHDATA="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
if [ $DEBUG == "true" ]; then echo "## SCRIPT rfid_trigger_play.sh ($NOW) ##" >> $PATHDATA/../logs/debug.log; fi

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
fi
# 2. then|or read value from file
AUDIOFOLDERSPATH=`cat $PATHDATA/../settings/Audio_Folders_Path`

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
    FOLDER="${i#*=}"
    ;;
esac
done
if [ $DEBUG == "true" ]; then echo "VAR CARDID: $CARDID" >> $PATHDATA/../logs/debug.log; fi
if [ $DEBUG == "true" ]; then echo "VAR FOLDER: $FOLDER" >> $PATHDATA/../logs/debug.log; fi

##################################################################
# Check if we got the card ID or the audio folder from the prompt.
# Sloppy error check, because we assume the best.
if [ "$CARDID" ]; then
    # we got the card ID
    # If you want to see the CARDID printed, uncomment the following line
    # echo CARDID = $CARDID

    # Add info into the log, making it easer to monitor cards 
    echo "Card ID '$CARDID' was used at '$NOW'." > $PATHDATA/../shared/latestID.txt
    echo "$CARDID" > $PATHDATA/../settings/Latest_RFID
    if [ $DEBUG == "true" ]; then echo "Card ID '$CARDID' was used"   >> $PATHDATA/../logs/debug.log; fi

    # If the input is of 'special' use, don't treat it like a trigger to play audio.
    # Special uses are for example volume changes, skipping, muting sound.

    case $CARDID in 
	$CMDSHUFFLE)
            # toogles shuffle mode  (random on/off)
            $PATHDATA/playout_controls.sh -c=playershuffle
            ;;
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
		$ENABLEWIFI)
            $PATHDATA/playout_controls.sh -c=enablewifi
			;;
		$DISABLEWIFI)
            $PATHDATA/playout_controls.sh -c=disablewifi
			;;
        *)
            # We checked if the card was a special command, seems it wasn't.
            # Now we expect it to be a trigger for one or more audio file(s).
            # Let's look at the ID, write a bit of log information and then try to play audio.
        
            # Expected folder structure:
            #
            # $PATHDATA + /../shared/audiofolders/ + $FOLDER
            # Note: $FOLDER is read from a file inside 'shortcuts'.
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
                FOLDER=`cat $PATHDATA/../shared/shortcuts/$CARDID`
                # Add info into the log, making it easer to monitor cards
                echo "This ID has been used before." >> $PATHDATA/../shared/latestID.txt
                if [ $DEBUG == "true" ]; then echo "This ID has been used before."   >> $PATHDATA/../logs/debug.log; fi
            else
                # Human readable shortcut does not exists, so create one with the content $CARDID
                # this file can later be edited manually over the samba network
                echo "$CARDID" > $PATHDATA/../shared/shortcuts/$CARDID
                FOLDER=$CARDID
                # Add info into the log, making it easer to monitor cards
                echo "This ID was used for the first time." >> $PATHDATA/../shared/latestID.txt
                if [ $DEBUG == "true" ]; then echo "This ID was used for the first time."   >> $PATHDATA/../logs/debug.log; fi
            fi
            # Add info into the log, making it easer to monitor cards
            echo "The shortcut points to audiofolder '$FOLDER'." >> $PATHDATA/../shared/latestID.txt
            if [ $DEBUG == "true" ]; then echo "The shortcut points to audiofolder '$FOLDER'." >> $PATHDATA/../logs/debug.log; fi
            ;;
    esac
fi

##############################################################
# We should now have a folder name with the audio files.
# Either from prompt of from the card ID processing above
# Sloppy error check, because we assume the best.

if [ $DEBUG == "true" ]; then echo "# Attempting to play: $AUDIOFOLDERSPATH/$FOLDER" >> $PATHDATA/../logs/debug.log; fi

if [ "$FOLDER" ]; then

    # if we play a folder the first time, add some sensible information to the folder.conf
    if [ ! -f "$AUDIOFOLDERSPATH/$FOLDER/folder.conf" ]; then
        # now we create a default folder.conf file by calling this script
        # with the command param createDefaultFolderConf
        # (see script for details)
        # the $FOLDER would not need to be passed on, because it is already set in this script
        # see inc.writeFolderConfig.sh for details
        . $PATHDATA/inc.writeFolderConfig.sh -c=createDefaultFolderConf -d="$FOLDER"
    fi

    # Save position (to catch playing and paused audio) for resume and clear the playlist -> audio off
    # Is has to be sudo as daemon_rfid_reader.py doesn't call this script with sudo
    # and this produces an error while saving folder.conf
	
    # Before we create a new playlist, we remove the old one from the folder.
    # It's a workaround for resume playing as mpd doesn't know how its current playlist is named,
    # so we only want the current playlist in the "mpc lsplaylists" output.
    mpc lsplaylists | \
    while read i
    do
        mpc rm "$i"
    done

    # if a folder $FOLDER exists, play content
    if [ -d "$AUDIOFOLDERSPATH/$FOLDER" ]
    then

        # set path to playlist
        PLAYLISTPATH="/tmp/$FOLDER.m3u"
        if [ $DEBUG == "true" ]; then echo "VAR FOLDER: $FOLDER"   >> $PATHDATA/../logs/debug.log; fi
        if [ $DEBUG == "true" ]; then echo "VAR PLAYLISTPATH: $PLAYLISTPATH"   >> $PATHDATA/../logs/debug.log; fi

        # prep to check "if same playlist playing or paused" later
        if [ $DEBUG == "true" ]; then mpc status; fi
        mpd_status="offline"
        if mpc status | awk 'NR==2' | grep playing > /dev/null;
        then 
            mpd_status="playing"
        fi
        if mpc status | awk 'NR==2' | grep paused > /dev/null;
        then 
            mpd_status="paused"
        fi
        if [ $DEBUG == "true" ]; then echo "VAR mpd_status: $mpd_status" >> $PATHDATA/../logs/debug.log; fi

        # Check if we have something special to do
        # Read content file names of folder into string
        SPECIALFORMAT=$(ls "$AUDIOFOLDERSPATH/$FOLDER" | grep .txt)
        if [ $DEBUG == "true" ]; then echo "VAR SPECIALFORMAT: $SPECIALFORMAT"   >> $PATHDATA/../logs/debug.log; fi

        # the following switch can be extended with other 'special' formats which require
        # more complex action than just piping the folder content into a playlist
        if [ $DEBUG == "true" ]; then echo "CHECK Something special to do?" >> $PATHDATA/../logs/debug.log; fi
        case $SPECIALFORMAT in
            "podcast.txt")
                # Podcast
                PODCASTURL=`cat "$AUDIOFOLDERSPATH/$FOLDER/podcast.txt"`
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
                cat "$AUDIOFOLDERSPATH/$FOLDER/livestream.txt" > "$PLAYLISTPATH"
                if [ $DEBUG == "true" ]
                then
                    echo "Livestream $PLAYLISTPATH"   >> $PATHDATA/../logs/debug.log
                fi
            ;;
            *)
                # Nothing special to do, folder with audio files
                # write playlist to file using the same name as the folder with ending .m3u
                # wrap $PLAYLIST string in "" to keep line breaks
        	# cd to $AUDIOFOLDERSPATH as mpd accepts only filepaths relative to its music folder
        	# or starting with file:// (e.g. file:///home/pi...)
                cd $AUDIOFOLDERSPATH
                find "$FOLDER" -type f | sort -f > "$PLAYLISTPATH"
                if [ $DEBUG == "true" ]; then echo "Nothing special $PLAYLISTPATH" >> $PATHDATA/../logs/debug.log; fi
            ;;
        esac
        
        # Now we know what we will be playing -> start playing (or pausing?)!
        
        # read the latest folder into var
        Latest_Folder_Played=`cat $PATHDATA/../settings/Latest_Folder_Played`
        # now we can write folder name and write RFID to file 
        # because webapp is also pushed from htdocs/inc.header.php to this script,
        # but without a CARDID, only -d (FOLDER), we need to check IF CARDID is set.
        if [ "$CARDID" ]; then
            sudo echo "${CARDID}" > $PATHDATA/../settings/Latest_RFID_Played
            sudo chmod 777 $PATHDATA/../settings/Latest_RFID_Played
        fi
        # write foldername triggered by RFID to file 
        sudo echo "${FOLDER}" > $PATHDATA/../settings/Latest_Folder_Played
        sudo chmod 777 $PATHDATA/../settings/Latest_Folder_Played
        if [ $DEBUG == "true" ]; then echo "echo ${FOLDER} > $PATHDATA/../settings/Latest_Folder_Played" >> $PATHDATA/../logs/debug.log; fi
        if [ $DEBUG == "true" ]; then echo "VAR Latest_Folder_Played: $Latest_Folder_Played" >> $PATHDATA/../logs/debug.log; fi

        # 1. MPD playing
        if [ $mpd_status == "playing" ]
        then
            if [ $DEBUG == "true" ]; then echo "1. MPD playing" >> $PATHDATA/../logs/debug.log; fi
            # 1.1 IF new folder given ("$Latest_Folder_Played" != "$FOLDER")
            if [ $DEBUG == "true" ]; then echo "1.1 CHECK Latest_Folder_Played ($Latest_Folder_Played) != FOLDER($FOLDER)" >> $PATHDATA/../logs/debug.log; fi
            if [ "$Latest_Folder_Played" != "$FOLDER" ]
            then
                # 1.1.1 YES => stop current && start (resume) new
                if [ $DEBUG == "true" ]; then echo "1.1.1 CHECK TRUE => resume_play.sh -c=savepos -d=${Latest_Folder_Played} playout_controls.sh -c=playlistaddplay -v=${FOLDER}" >> $PATHDATA/../logs/debug.log; fi
                sudo $PATHDATA/resume_play.sh -c=savepos -d="${Latest_Folder_Played}"
                sudo $PATHDATA/playout_controls.sh -c=playlistaddplay -v="${FOLDER}" &>/dev/null
            else 
                # 1.1.2 NO => stop current
                if [ $DEBUG == "true" ]; then echo "1.1.2 CHECK FALSE => playout_controls.sh -c=playerstop" >> $PATHDATA/../logs/debug.log; fi
                sudo $PATHDATA/playout_controls.sh -c=playerstop &>/dev/null
            fi
        fi
        
        # 2. MPD paused
        if [ $mpd_status == "paused" ]
        then
            if [ $DEBUG == "true" ]; then echo "2. MPD paused" >> $PATHDATA/../logs/debug.log; fi
            # 2.1 IF new folder given ("$Latest_Folder_Played" != "$FOLDER")
            if [ $DEBUG == "true" ]; then echo "2.1 CHECK Latest_Folder_Played ($Latest_Folder_Played) != FOLDER($FOLDER)" >> $PATHDATA/../logs/debug.log; fi
            if [ "$Latest_Folder_Played" != "$FOLDER" ]
            then
                # 2.1.1 YES => stop current && start (resume) new
                if [ $DEBUG == "true" ]; then echo "2.1.1 CHECK TRUE => resume_play.sh -c=savepos -d=${Latest_Folder_Played} playout_controls.sh -c=playlistaddplay -v=${FOLDER}" >> $PATHDATA/../logs/debug.log; fi
                sudo $PATHDATA/resume_play.sh -c=savepos -d="${Latest_Folder_Played}"
                sudo $PATHDATA/playout_controls.sh -c=playlistaddplay -v="${FOLDER}" &>/dev/null
            else 
                # 2.1.2 NO => play (resume) current
                if [ $DEBUG == "true" ]; then echo "2.1.2 CHECK FALSE => playout_controls.sh -c=playerpause" >> $PATHDATA/../logs/debug.log; fi
                sudo $PATHDATA/playout_controls.sh -c=playerpause &>/dev/null
            fi
        fi
        
        # 3. MPD offline
        if [ $mpd_status == "offline" ]
        then
            if [ $DEBUG == "true" ]; then echo "3. MPD offline" >> $PATHDATA/../logs/debug.log; fi
            # 3.1 play (resume) current
            if [ $DEBUG == "true" ]; then echo "3.1 play (resume) current" >> $PATHDATA/../logs/debug.log; fi
            sudo $PATHDATA/playout_controls.sh -c=playlistaddplay -v="${FOLDER}" &>/dev/null
        fi

    else
        if [ $DEBUG == "true" ]; then echo "Path not found $AUDIOFOLDERSPATH/$FOLDER" >> $PATHDATA/../logs/debug.log; fi
    fi
fi
