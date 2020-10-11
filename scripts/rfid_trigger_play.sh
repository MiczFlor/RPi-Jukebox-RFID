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
# ./rfid_trigger_play.sh -d='foldername'
# or
# ./rfid_trigger_play.sh --dir='foldername'
#
# or for recursive play of sudfolders
# ./rfid_trigger_play.sh -d='foldername' -v=recursive

# ADD / EDIT RFID CARDS TO CONTROL THE PHONIEBOX
# All controls are assigned to RFID cards in this
# file:
# settings/rfid_trigger_play.conf
# Please consult this file for more information.
# Do NOT edit anything in this file.

# Set the date and time of now
NOW=`date +%Y-%m-%d.%H:%M:%S`

# The absolute path to the folder whjch contains all the scripts.
# Unless you are working with symlinks, leave the following line untouched.
PATHDATA="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

#############################################################
# $DEBUG TRUE|FALSE
# Read debug logging configuration file
. $PATHDATA/../settings/debugLogging.conf

if [ "${DEBUG_rfid_trigger_play_sh}" == "TRUE" ]; then echo "########### SCRIPT rfid_trigger_play.sh ($NOW) ##" >> $PATHDATA/../logs/debug.log; fi

# create the configuration file from sample - if it does not exist
if [ ! -f $PATHDATA/../settings/rfid_trigger_play.conf ]; then
    cp $PATHDATA/../settings/rfid_trigger_play.conf.sample $PATHDATA/../settings/rfid_trigger_play.conf
    # change the read/write so that later this might also be editable through the web app
    sudo chown -R pi:www-data $PATHDATA/../settings/rfid_trigger_play.conf
    sudo chmod -R 775 $PATHDATA/../settings/rfid_trigger_play.conf
fi

###########################################################
# Read global configuration file (and create is not exists)
# create the global configuration file from single files - if it does not exist
if [ ! -f $PATHDATA/../settings/global.conf ]; then
    . inc.writeGlobalConfig.sh
fi
. $PATHDATA/../settings/global.conf
###########################################################

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
    if [ "${DEBUG_rfid_trigger_play_sh}" == "TRUE" ]; then echo "Card ID '$CARDID' was used" >> $PATHDATA/../logs/debug.log; fi

    # If the input is of 'special' use, don't treat it like a trigger to play audio.
    # Special uses are for example volume changes, skipping, muting sound.

    case $CARDID in
	    $CMDSHUFFLE)
            # toggles shuffle mode  (random on/off)
            $PATHDATA/playout_controls.sh -c=playershuffle
            ;;
        $CMDMAXVOL30)
            # limit volume to 30%
            $PATHDATA/playout_controls.sh -c=setmaxvolume -v=30
            ;;
        $CMDMAXVOL50)
            # limit volume to 50%
            $PATHDATA/playout_controls.sh -c=setmaxvolume -v=50
            ;;
        $CMDMAXVOL75)
            # limit volume to 75%
            $PATHDATA/playout_controls.sh -c=setmaxvolume -v=75
            ;;
        $CMDMAXVOL80)
            # limit volume to 80%
            $PATHDATA/playout_controls.sh -c=setmaxvolume -v=80
            ;;
        $CMDMAXVOL85)
            # limit volume to 85%
            $PATHDATA/playout_controls.sh -c=setmaxvolume -v=85
            ;;
        $CMDMAXVOL90)
            # limit volume to 90%
            $PATHDATA/playout_controls.sh -c=setmaxvolume -v=90
            ;;
        $CMDMAXVOL95)
            # limit volume to 95%
            $PATHDATA/playout_controls.sh -c=setmaxvolume -v=95
            ;;
        $CMDMAXVOL100)
            # limit volume to 100%
            $PATHDATA/playout_controls.sh -c=setmaxvolume -v=100
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
        $CMDVOL80)
            # amixer sset 'PCM' 80%
            $PATHDATA/playout_controls.sh -c=setvolume -v=80
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
            # play next track in playlist
            $PATHDATA/playout_controls.sh -c=playernext
            ;;
        $CMDPREV)
            # play previous track in playlist
            # echo "prev" | nc.openbsd -w 1 localhost 4212
            sudo $PATHDATA/playout_controls.sh -c=playerprev
            #/usr/bin/sudo /home/pi/RPi-Jukebox-RFID/scripts/playout_controls.sh -c=playerprev
            ;;
        $CMDREWIND)
            # play the first track in playlist
            sudo $PATHDATA/playout_controls.sh -c=playerrewind
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
        $TOGGLEWIFI)
            $PATHDATA/playout_controls.sh -c=togglewifi
            ;;
        $CMDPLAYCUSTOMPLS)
            $PATHDATA/playout_controls.sh -c=playlistaddplay -v="PhonieCustomPLS" -d="PhonieCustomPLS"
            ;;
        $RECORDSTART600)
            #start recorder for -v seconds
            $PATHDATA/playout_controls.sh -c=recordstart -v=600
            ;;
        $RECORDSTART60)
            #start recorder for -v seconds
            $PATHDATA/playout_controls.sh -c=recordstart -v=60
            ;;
        $RECORDSTART10)
            #start recorder for -v seconds
            $PATHDATA/playout_controls.sh -c=recordstart -v=10
            ;;
        $RECORDSTOP)
            $PATHDATA/playout_controls.sh -c=recordstop
            ;;
        $RECORDPLAYBACKLATEST)
            $PATHDATA/playout_controls.sh -c=recordplaybacklatest
            ;;
        $CMDREADWIFIIP)
            $PATHDATA/playout_controls.sh -c=readwifiipoverspeaker
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
                if [ "${DEBUG_rfid_trigger_play_sh}" == "TRUE" ]; then echo "This ID has been used before."   >> $PATHDATA/../logs/debug.log; fi
            else
                # Human readable shortcut does not exists, so create one with the content $CARDID
                # this file can later be edited manually over the samba network
                echo "$CARDID" > $PATHDATA/../shared/shortcuts/$CARDID
                FOLDER=$CARDID
                # Add info into the log, making it easer to monitor cards
                echo "This ID was used for the first time." >> $PATHDATA/../shared/latestID.txt
                if [ "${DEBUG_rfid_trigger_play_sh}" == "TRUE" ]; then echo "This ID was used for the first time."   >> $PATHDATA/../logs/debug.log; fi
            fi
            # Add info into the log, making it easer to monitor cards
            echo "The shortcut points to audiofolder '$FOLDER'." >> $PATHDATA/../shared/latestID.txt
            if [ "${DEBUG_rfid_trigger_play_sh}" == "TRUE" ]; then echo "The shortcut points to audiofolder '$FOLDER'." >> $PATHDATA/../logs/debug.log; fi
            ;;
    esac
fi

##############################################################
# We should now have a folder name with the audio files.
# Either from prompt of from the card ID processing above
# Sloppy error check, because we assume the best.

if [ "${DEBUG_rfid_trigger_play_sh}" == "TRUE" ]; then echo "# Attempting to play: $AUDIOFOLDERSPATH/$FOLDER" >> $PATHDATA/../logs/debug.log; fi
if [ "${DEBUG_rfid_trigger_play_sh}" == "TRUE" ]; then echo "# Type of play \$VALUE: $VALUE" >> $PATHDATA/../logs/debug.log; fi

# check if
# - $FOLDER is not empty (! -z "$FOLDER")
# - AND (-a)
# - $FOLDER is set (! -z ${FOLDER+x})
# - AND (-a)
# - and points to existing directory (-d "${AUDIOFOLDERSPATH}/${FOLDER}")
if [ ! -z "$FOLDER" -a ! -z ${FOLDER+x} -a -d "${AUDIOFOLDERSPATH}/${FOLDER}" ]; then

    if [ "${DEBUG_rfid_trigger_play_sh}" == "TRUE" ]; then echo "\$FOLDER set, not empty and dir exists: ${AUDIOFOLDERSPATH}/${FOLDER}" >> $PATHDATA/../logs/debug.log; fi

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
    # this might need to go? resume not working... echo ${FOLDER} > $PATHDATA/../settings/Latest_Folder_Played
    if [ "${DEBUG_rfid_trigger_play_sh}" == "TRUE" ]; then echo "  Var \$LASTFOLDER: $LASTFOLDER" >> $PATHDATA/../logs/debug.log; fi
    if [ "${DEBUG_rfid_trigger_play_sh}" == "TRUE" ]; then echo "  Var \$LASTPLAYLIST: $LASTPLAYLIST" >> $PATHDATA/../logs/debug.log; fi
    if [ "${DEBUG_rfid_trigger_play_sh}" == "TRUE" ]; then echo "Checking 'recursive' list? VAR \$VALUE: $VALUE" >> $PATHDATA/../logs/debug.log; fi

    if [ "$VALUE" == "recursive" ]; then
        # set path to playlist
        # replace subfolder slashes with " % "
        PLAYLISTPATH="${PLAYLISTSFOLDERPATH}/${FOLDER//\//\ %\ }-%RCRSV%.m3u"
        PLAYLISTNAME="${FOLDER//\//\ %\ }-%RCRSV%"
        $PATHDATA/playlist_recursive_by_folder.php --folder "${FOLDER}" --list 'recursive' > "${PLAYLISTPATH}"
        if [ "${DEBUG_rfid_trigger_play_sh}" == "TRUE" ]; then echo "recursive? YES"   >> $PATHDATA/../logs/debug.log; fi
        if [ "${DEBUG_rfid_trigger_play_sh}" == "TRUE" ]; then echo "$PATHDATA/playlist_recursive_by_folder.php --folder \"${FOLDER}\" --list 'recursive' > \"${PLAYLISTPATH}\""   >> $PATHDATA/../logs/debug.log; fi
    else
        # set path to playlist
        # replace subfolder slashes with " % "
        PLAYLISTPATH="${PLAYLISTSFOLDERPATH}/${FOLDER//\//\ %\ }.m3u"
        PLAYLISTNAME="${FOLDER//\//\ %\ }"
        $PATHDATA/playlist_recursive_by_folder.php --folder "${FOLDER}" > "${PLAYLISTPATH}"
        if [ "${DEBUG_rfid_trigger_play_sh}" == "TRUE" ]; then echo "recursive? NO"   >> $PATHDATA/../logs/debug.log; fi
        if [ "${DEBUG_rfid_trigger_play_sh}" == "TRUE" ]; then echo "$PATHDATA/playlist_recursive_by_folder.php --folder \"${FOLDER}\" > \"${PLAYLISTPATH}\""   >> $PATHDATA/../logs/debug.log; fi
    fi

    # Second Swipe value
    if [ "${DEBUG_rfid_trigger_play_sh}" == "TRUE" ]; then echo "  Var \$SECONDSWIPE: ${SECONDSWIPE}"   >> $PATHDATA/../logs/debug.log; fi
    # Playlist name
    if [ "${DEBUG_rfid_trigger_play_sh}" == "TRUE" ]; then echo "  Var \$PLAYLISTNAME: ${PLAYLISTNAME}"   >> $PATHDATA/../logs/debug.log; fi
    if [ "${DEBUG_rfid_trigger_play_sh}" == "TRUE" ]; then echo "  Var \$LASTPLAYLIST: ${LASTPLAYLIST}"   >> $PATHDATA/../logs/debug.log; fi

    # Setting a VAR to start "play playlist from start"
    # This will be changed in the following checks "if this is the second swipe"
    PLAYPLAYLIST=yes

    # Check if the second swipe happened
    # - The same playlist is cued up ("$LASTPLAYLIST" == "$PLAYLISTNAME")
    if [ "$LASTPLAYLIST" == "$PLAYLISTNAME" ]
    then
        if [ "${DEBUG_rfid_trigger_play_sh}" == "TRUE" ]; then echo "  Second Swipe DID happen: \$LASTPLAYLIST == \$PLAYLISTNAME"   >> $PATHDATA/../logs/debug.log; fi

        # check if
        # - $SECONDSWIPE is set to toggle pause/play ("$SECONDSWIPE" == "PAUSE")
        # - AND (-a)
        # - check the length of the playlist, if =0 then it was cleared before, a state, which should only
        #   be possible after a reboot ($PLLENGTH -gt 0)
        PLLENGTH=$(echo -e "status\nclose" | nc -w 1 localhost 6600 | grep -o -P '(?<=playlistlength: ).*')
        if [ $PLLENGTH -eq 0 ]
        then
            # after a reboot we want to play the playlist once no matter what the setting is
            if [ "${DEBUG_rfid_trigger_play_sh}" == "TRUE" ]; then echo "  Take second wipe as first after fresh boot" >> $PATHDATA/../logs/debug.log; fi
        elif [ "$SECONDSWIPE" == "PAUSE" -a $PLLENGTH -gt 0 ]
        then
            # The following involves NOT playing the playlist, so we set:
            PLAYPLAYLIST=no

            STATE=$(echo -e "status\nclose" | nc -w 1 localhost 6600 | grep -o -P '(?<=state: ).*')
            if [ $STATE == "play" ]
            then
                if [ "${DEBUG_rfid_trigger_play_sh}" == "TRUE" ]; then echo "  MPD playing, pausing the player" >> $PATHDATA/../logs/debug.log; fi
                sudo $PATHDATA/playout_controls.sh -c=playerpause &>/dev/null
            else
                if [ "${DEBUG_rfid_trigger_play_sh}" == "TRUE" ]; then echo "MPD not playing, start playing" >> $PATHDATA/../logs/debug.log; fi
                sudo $PATHDATA/playout_controls.sh -c=playerplay &>/dev/null
            fi
            if [ "${DEBUG_rfid_trigger_play_sh}" == "TRUE" ]; then echo "  Completed: toggle pause/play" >> $PATHDATA/../logs/debug.log; fi
        elif [ "$SECONDSWIPE" == "PLAY" -a $PLLENGTH -gt 0 ]
        then
            # The following involves NOT playing the playlist, so we set:
            PLAYPLAYLIST=no
            sudo $PATHDATA/playout_controls.sh -c=playerplay &>/dev/null
            if [ "${DEBUG_rfid_trigger_play_sh}" == "TRUE" ]; then echo "  Completed: Resume playback" >> $PATHDATA/../logs/debug.log; fi
        elif [ "$SECONDSWIPE" == "NOAUDIOPLAY" ]
        then
            # The following involves NOT playing the playlist, so we set:
            PLAYPLAYLIST=no
            # following needs testing (see https://github.com/chbuehlmann/RPi-Jukebox-RFID/issues/914)
            # Special case for NOAUDIOPLAY because once the playlist has finished,
            # it needs to be noted by the system that the second swipe is like a *first* swipe.
            currentSong=`mpc current`
            if [[ -z "$currentSong" ]]; then
                #end of playlist (EOPL) reached. Ignore last played playlist
                PLAYPLAYLIST=yes
            fi

            # "$SECONDSWIPE" == "NOAUDIOPLAY"
            # "$LASTPLAYLIST" == "$PLAYLISTNAME" => same playlist triggered again
            # => do nothing
            # echo "do nothing" > /dev/null 2>&1
            if [ "${DEBUG_rfid_trigger_play_sh}" == "TRUE" ]; then echo "  Completed: do nothing" >> $PATHDATA/../logs/debug.log; fi
        elif [ "$SECONDSWIPE" == "SKIPNEXT" ]
        then
            # We will not play the playlist but skip to the next track:
            PLAYPLAYLIST=skipnext
            if [ "${DEBUG_rfid_trigger_play_sh}" == "TRUE" ]; then echo "  Completed: skip next track" >> $PATHDATA/../logs/debug.log; fi
        fi
    fi
    # now we check if we are still on for playing what we got passed on:
    if [ "$PLAYPLAYLIST" == "yes" ]
    then
        if [ "${DEBUG_rfid_trigger_play_sh}" == "TRUE" ]; then echo "We must play the playlist no matter what: \$PLAYPLAYLIST == yes"   >> $PATHDATA/../logs/debug.log; fi

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
        #   $PATHDATA/playlist_recursive_by_folder.php --folder "${FOLDER}" --list 'recursive'

        if [ "${DEBUG_rfid_trigger_play_sh}" == "TRUE" ]; then echo "  VAR FOLDER: $FOLDER"   >> $PATHDATA/../logs/debug.log; fi
        if [ "${DEBUG_rfid_trigger_play_sh}" == "TRUE" ]; then echo "  VAR PLAYLISTPATH: $PLAYLISTPATH"   >> $PATHDATA/../logs/debug.log; fi

		# save position of current playing list "stop"
		$PATHDATA/playout_controls.sh -c=playerstop
		# play playlist
        # the variable passed on to play is the playlist name -v (NOT the folder name)
        # because (see above) a folder can be played recursively (including subfolders) or flat (only containing files)
        # load new playlist and play
        $PATHDATA/playout_controls.sh -c=playlistaddplay -v="${PLAYLISTNAME}" -d="${FOLDER}"
        if [ "${DEBUG_rfid_trigger_play_sh}" == "TRUE" ]; then echo "  Command: $PATHDATA/playout_controls.sh -c=playlistaddplay -v=\"${PLAYLISTNAME}\" -d=\"${FOLDER}\"" >> $PATHDATA/../logs/debug.log; fi
        # save latest playlist not to file
        sudo echo ${PLAYLISTNAME} > $PATHDATA/../settings/Latest_Playlist_Played
        sudo chown pi:www-data $PATHDATA/../settings/Latest_Playlist_Played
        sudo chmod 777 $PATHDATA/../settings/Latest_Playlist_Played
    fi
    if [ "$PLAYPLAYLIST" == "skipnext" ]
    then
        if [ "${DEBUG_rfid_trigger_play_sh}" == "TRUE" ]; then echo "Skip to the next track in the playlist: \$PLAYPLAYLIST == skipnext"   >> $PATHDATA/../logs/debug.log; fi
        if [ "${DEBUG_rfid_trigger_play_sh}" == "TRUE" ]; then echo "  VAR FOLDER: $FOLDER"   >> $PATHDATA/../logs/debug.log; fi
        if [ "${DEBUG_rfid_trigger_play_sh}" == "TRUE" ]; then echo "  VAR PLAYLISTPATH: $PLAYLISTPATH"   >> $PATHDATA/../logs/debug.log; fi

        if [ "${DEBUG_rfid_trigger_play_sh}" == "TRUE" ]; then echo "  Command: $PATHDATA/playout_controls.sh -c=playernext" >> $PATHDATA/../logs/debug.log; fi
        $PATHDATA/playout_controls.sh -c=playernext
    fi
else
    if [ "${DEBUG_rfid_trigger_play_sh}" == "TRUE" ]; then echo "Path not found $AUDIOFOLDERSPATH/$FOLDER" >> $PATHDATA/../logs/debug.log; fi
fi
