#!/bin/bash

# Reads the card ID or the folder name with audio files
# from the command line (see Usage).
# Then attempts to get the folder name from the card ID
# or play audio folder content directly
#
# Usage for card ID
# ./rfid_trigger_play.sh -i=1234567890
# or
# ./rfid_trigger_play.sh --cardid=1234567890
#
# For folder names:
# ./rfid_trigger_play.sh -d=foldername
# or
# ./rfid_trigger_play.sh --dir=foldername
#
# or for recursive play of sudfolders
# ./rfid_trigger_play.sh -d=foldername -v=recursive

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
if [ $DEBUG == "true" ]; then echo "########### SCRIPT rfid_trigger_play.sh ($NOW) ##" >> $PATHDATA/../logs/debug.log; fi

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

# File extension for playlists
# This needs to be m3u by default and m3u8 for spotify integration
# 1. create a default if file does not exist
if [ ! -f $PATHDATA/../settings/Playlists_File_Extension ]; then
    echo "m3u" > $PATHDATA/../settings/Playlists_File_Extension
    chmod 777 $PATHDATA/../settings/Playlists_File_Extension
fi
# 2. then|or read value from file
PLAYLISTSFILEEXTENSION=`cat $PATHDATA/../settings/Playlists_File_Extension`

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

# Read configuration file
. $PATHDATA/../settings/rfid_trigger_play.conf

# Get args from command line (see Usage above)
# see following file for details:
. $PATHDATA/inc.readArgsFromCommandLine.sh

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
    if [ $DEBUG == "true" ]; then echo "Card ID '$CARDID' was used" >> $PATHDATA/../logs/debug.log; fi

    # If the input is of 'special' use, don't treat it like a trigger to play audio.
    # Special uses are for example volume changes, skipping, muting sound.

    case $CARDID in 
	    $CMDSHUFFLE)
            # toggles shuffle mode  (random on/off)
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
        $CMDSEEKFORW)
            # jump 15 seconds ahead
            $PATHDATA/playout_controls.sh -c=playerseek -v=+15
            ;;
        $CMDSEEKBACK)
            # jump 15 seconds back
            $PATHDATA/playout_controls.sh -c=playerseek -v=-15
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
        $STARTRECORD600)
            #start recorder for -v seconds
            $PATHDATA/playout_controls.sh -c=startrecord -v=600			             
            ;;
        $STOPRECORD)
            $PATHDATA/playout_controls.sh -c=stoprecord
            ;;
        *)
            # We checked if the card was a special command, seems it wasn't.
            # Now we expect it to be a trigger for one or more audio file(s).
            # Let's look at the ID, write a bit of log information and then try to play audio.
        
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
if [ $DEBUG == "true" ]; then echo "# Type of play \$VALUE: $VALUE" >> $PATHDATA/../logs/debug.log; fi

# check if 
# - $FOLDER is not empty (! -z "$FOLDER") 
# - AND (-a) 
# - $FOLDER is set (! -z ${FOLDER+x})
# - AND (-a) 
# - and points to existing directory (-d "${AUDIOFOLDERSPATH}/${FOLDER}")
if [ ! -z "$FOLDER" -a ! -z ${FOLDER+x} -a -d "${AUDIOFOLDERSPATH}/${FOLDER}" ]; then

    if [ $DEBUG == "true" ]; then echo "\$FOLDER set, not empty and dir exists: ${AUDIOFOLDERSPATH}/${FOLDER}" >> $PATHDATA/../logs/debug.log; fi

    # if we play a folder the first time, add some sensible information to the folder.conf
    if [ ! -f "${AUDIOFOLDERSPATH}/${FOLDER}/folder.conf" ]; then
        # now we create a default folder.conf file by calling this script
        # with the command param createDefaultFolderConf
        # (see script for details)
        # the $FOLDER would not need to be passed on, because it is already set in this script
        # see inc.writeFolderConfig.sh for details
        . $PATHDATA/inc.writeFolderConfig.sh -c=createDefaultFolderConf -d="${FOLDER}"
    fi

    # get the name of the last folder played. As mpd doesn't store the name of the last
    # playlist, we have to keep track of it via the Latest_Folder_Played file
    LASTFOLDER=$(cat $PATHDATA/../settings/Latest_Folder_Played)
    LASTPLAYLIST=$(cat $PATHDATA/../settings/Latest_Playlist_Played)
    if [ $DEBUG == "true" ]; then echo "Var \$LASTFOLDER: $LASTFOLDER" >> $PATHDATA/../logs/debug.log; fi
    if [ $DEBUG == "true" ]; then echo "Var \$LASTPLAYLIST: $LASTPLAYLIST" >> $PATHDATA/../logs/debug.log; fi    
    if [ $DEBUG == "true" ]; then echo "Checking 'recursive' list? VAR \$VALUE: $VALUE" >> $PATHDATA/../logs/debug.log; fi

    if [ "$VALUE" == "recursive" ]; then
        # set path to playlist
        # replace subfolder slashes with " % "
        PLAYLISTPATH="${PLAYLISTSFOLDERPATH}/${FOLDER//\//\ %\ } %RCRSV%.${PLAYLISTSFILEEXTENSION}"
        PLAYLISTNAME="${FOLDER//\//\ %\ } %RCRSV%"
        $PATHDATA/playlist_recursive_by_folder.php folder="${FOLDER}" list='recursive' > "${PLAYLISTPATH}"
        if [ $DEBUG == "true" ]; then echo "$PATHDATA/playlist_recursive_by_folder.php folder=\"${FOLDER}\" list='recursive' > \"${PLAYLISTPATH}\""   >> $PATHDATA/../logs/debug.log; fi
    else
        # set path to playlist
        # replace subfolder slashes with " % "
        PLAYLISTPATH="${PLAYLISTSFOLDERPATH}/${FOLDER//\//\ %\ }.${PLAYLISTSFILEEXTENSION}"
        PLAYLISTNAME="${FOLDER//\//\ %\ }"
        $PATHDATA/playlist_recursive_by_folder.php folder="${FOLDER}" > "${PLAYLISTPATH}"
        if [ $DEBUG == "true" ]; then echo "$PATHDATA/playlist_recursive_by_folder.php folder=\"${FOLDER}\" > \"${PLAYLISTPATH}\""   >> $PATHDATA/../logs/debug.log; fi
    fi

    # Second Swipe value
    if [ $DEBUG == "true" ]; then echo "Var \$SECONDSWIPE: ${SECONDSWIPE}"   >> $PATHDATA/../logs/debug.log; fi
    # Playlist name
    if [ $DEBUG == "true" ]; then echo "Var \$PLAYLISTNAME: ${PLAYLISTNAME}"   >> $PATHDATA/../logs/debug.log; fi
    
    # Setting a VAR to start "play playlist from start"
    # This will be changed in the following checks "if this is the second swipe"
    PLAYPLAYLIST=yes
    
    # Check if the second swipe happened
    # - The same playlist is cued up ("$LASTPLAYLIST" == "$PLAYLISTNAME")
    if [ "$LASTPLAYLIST" == "$PLAYLISTNAME" ]
    then
        if [ $DEBUG == "true" ]; then echo "Second Swipe DID happen: \$LASTPLAYLIST == \$PLAYLISTNAME"   >> $PATHDATA/../logs/debug.log; fi
        
        # check if 
        # - $SECONDSWIPE is set to toggle pause/play ("$SECONDSWIPE" == "PAUSE") 
        # - AND (-a)
        # - check the length of the playlist, if =0 then it was cleared before, a state, which should only
        #   be possible after a reboot ($PLLENGTH -gt 0)
        PLLENGTH=$(echo -e "status\nclose" | nc -w 1 localhost 6600 | grep -o -P '(?<=playlistlength: ).*')
        if [ "$SECONDSWIPE" == "PAUSE" -a $PLLENGTH -gt 0 ]
        then
            # The following involves NOT playing the playlist, so we set: 
            PLAYPLAYLIST=no
        
            STATE=$(echo -e "status\nclose" | nc -w 1 localhost 6600 | grep -o -P '(?<=state: ).*')
            if [ $STATE == "play" ]
            then
                if [ $DEBUG == "true" ]; then echo "MPD playing, pausing the player" >> $PATHDATA/../logs/debug.log; fi
                sudo $PATHDATA/playout_controls.sh -c=playerpause &>/dev/null
            else
                if [ $DEBUG == "true" ]; then echo "MPD not playing, start playing" >> $PATHDATA/../logs/debug.log; fi
                sudo $PATHDATA/playout_controls.sh -c=playerplay &>/dev/null
            fi
            if [ $DEBUG == "true" ]; then echo "Completed: toggle pause/play" >> $PATHDATA/../logs/debug.log; fi
        elif [ "$SECONDSWIPE" == "NOAUDIOPLAY" ]
        then
            # The following involves NOT playing the playlist, so we set: 
            PLAYPLAYLIST=no

            # "$SECONDSWIPE" == "NOAUDIOPLAY"
            # "$LASTPLAYLIST" == "$PLAYLISTNAME" => same playlist triggered again 
            # => do nothing
            # echo "do nothing" > /dev/null 2>&1
            if [ $DEBUG == "true" ]; then echo "Completed: do nothing" >> $PATHDATA/../logs/debug.log; fi
        fi
    fi
    # now we check if we are still on for playing what we got passed on:
    if [ "$PLAYPLAYLIST" == "yes" ]
    then
        if [ $DEBUG == "true" ]; then echo "We must play the playlist no matter what: \$PLAYPLAYLIST == yes"   >> $PATHDATA/../logs/debug.log; fi

        # Above we already checked if the folder exists -d "$AUDIOFOLDERSPATH/$FOLDER" 
        #
        # the process is as such - because of the recursive play option:
        # - each folder can be played. 
        # - a single folder will create a playlist with the same name as the folder
        # - because folders can live inside other folders, the relative path might contain
        #   slashes (e.g. audiobooks/Moby Dick/)
        # - because slashes can not be in the playlist name, slashes are replaced with " % "
        # - the "recursive" option means that the content of the folder AND all subfolders
        #   is being played
        # - in this case, the playlist is related to the same folder name, which means we need
        #   to make a different name for "recursive" playout
        # - a recursive playlist has the suffix " %RCRSV%" - keeping it cryptic to avoid clashes
        #   with a possible "real" name for a folder
        # - with this new logic, there are no more SPECIALFORMAT playlists. Live streams and podcasts
        #   are now all unfolded into the playlist
        # - creating the playlist is now done in the php script with parameters:
        #   $PATHDATA/playlist_recursive_by_folder.php folder="${FOLDER}" list='recursive'

        if [ $DEBUG == "true" ]; then echo "VAR FOLDER: $FOLDER"   >> $PATHDATA/../logs/debug.log; fi
        if [ $DEBUG == "true" ]; then echo "VAR PLAYLISTPATH: $PLAYLISTPATH"   >> $PATHDATA/../logs/debug.log; fi
       
        # load new playlist and play
        if [ $DEBUG == "true" ]; then echo "Command: $PATHDATA/playout_controls.sh -c=playlistaddplay -v=\"${PLAYLISTNAME}\" -d=\"${FOLDER}\"" >> $PATHDATA/../logs/debug.log; fi
		# play playlist
        # the variable passed on to play is NOT the folder name, but the playlist name
        # because (see above) a folder can be played recursively (including subfolders) or flat (only containing files)        
        $PATHDATA/playout_controls.sh -c=playlistaddplay -v="${PLAYLISTNAME}" -d="${FOLDER}"
    fi
    sudo echo ${PLAYLISTNAME} > $PATHDATA/../settings/Latest_Playlist_Played
    sudo chmod 777 $PATHDATA/../settings/Latest_Playlist_Played
else
    if [ $DEBUG == "true" ]; then echo "Path not found $AUDIOFOLDERSPATH/$FOLDER" >> $PATHDATA/../logs/debug.log; fi
fi
