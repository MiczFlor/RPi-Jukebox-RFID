#!/bin/bash

# This shell script contains all the functionality to control
# playout and change volume and the like.
# This script is called from the web app and the bash script.
# The purpose is to have all playout logic in one place, this
# makes further development and potential replacement of
# the playout player easier.

# USAGE EXAMPLES:
#
# shutdown RPi:
# ./playout_controls.sh -c=shutdown
#
# set volume to 80%
# ./playout_controls.sh -c=setvolume -v=80
#
# VALID COMMANDS:
# shutdown
# shutdownsilent
# shutdownafter
# shutdownvolumereduction
# reboot
# scan
# mute
# setvolume
# setmaxvolume
# setstartupvolume
# getstartupvolume
# setvolumetostartup
# volumeup
# volumedown
# getchapters
# getvolume
# getmaxvolume
# setvolstep
# getvolstep
# playerstop
# playerstopafter
# playernext
# playerprev
# playernextchapter
# playerprevchapter
# playerpause
# playerpauseforce
# playerplay
# playerremove
# playermoveup
# playermovedown
# playerreplay
# playerrepeat
# playershuffle
# playlistclear
# playlistaddplay
# playlistadd
# playlistappend
# playlistreset
# playsinglefile
# getidletime
# setidletime
# disablewifi
# enablewifi
# togglewifi
# recordstart
# recordstop
# recordplaylatest
# readwifiipoverspeaker
# bluetoothtoggle
# switchaudioiface

# The absolute path to the folder which contains all the scripts.
# Unless you are working with symlinks, leave the following line untouched.
PATHDATA="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

#############################################################
# $DEBUG TRUE|FALSE
# Read debug logging configuration file
. ${PATHDATA}/../settings/debugLogging.conf



######## UTILS #########

function log {
    if [ "${DEBUG_playout_controls_sh}" == "TRUE" ]; then
        echo "$1" >> ${PATHDATA}/../logs/debug.log;
    fi
}


function utils_shuffle_mode_off 
    SHUFFLE_STATUS=$(echo -e status\\nclose | nc -w 1 localhost 6600 | grep -o -P '(?<=random: ).*')
    if [ "$SHUFFLE_STATUS" == 1 ] ; then  mpc random off; fi
}







# Set the date and time of now
NOW=`date +%Y-%m-%d.%H:%M:%S`

log "########### SCRIPT playout_controls.sh ($NOW) ##"

###########################################################
# Read global configuration file (and create if not exists)
# create the global configuration file from single files - if it does not exist
if [ ! -f ${PATHDATA}/../settings/global.conf ]; then
    . ${PATHDATA}/inc.writeGlobalConfig.sh
fi
. ${PATHDATA}/../settings/global.conf
###########################################################

#################################
# path to file storing the current volume level
# this file does not need to exist
# it will be created or deleted by this script
VOLFILE=${PATHDATA}/../settings/Audio_Volume_Level

# path to file storing the current audio iFace name
IFACEFILE=${PATHDATA}/../settings/Audio_iFace_Name

#############################################################

# Get args from command line (see Usage above)
# Read the args passed on by the command line
# see following file for details:
. ${PATHDATA}/inc.readArgsFromCommandLine.sh

log "VAR COMMAND: ${COMMAND}"
log "VAR VALUE: ${VALUE}"

# Regex that declares commands for which the following code can be shortcut
# and we can immediately jump to the switch-case statement. Increases execution
# speed of these commands.
shortcutCommands="^(setvolume|volumedown|volumeup|mute)$"

# Run the code from this block only, if the current command is not in "shortcutCommands"
if [[ ! "$COMMAND" =~ $shortcutCommands ]]
then
    function sec_to_ms() {
        SECONDSPART="$(cut -d '.' -f 1 <<< "$1")"
        MILLISECONDSPART="$(cut -d '.' -f 2 <<< "$1")"
        MILLISECONDSPART_NORMALIZED="$(echo "$MILLISECONDSPART" | cut -c1-3 | sed 's/^0*//')"

        if [[ "" == "$SECONDSPART" ]]; then
            SECONDSPART="0"
        fi

        if [[ "" == "$MILLISECONDSPART_NORMALIZED" ]]; then
            MILLISECONDSPART_NORMALIZED="0"
        fi
        echo "$((${SECONDSPART} * 1000 + ${MILLISECONDSPART_NORMALIZED}))"
    }

    AUDIO_FOLDERS_PATH=$(cat "${PATHDATA}/../settings/Audio_Folders_Path")

    CURRENT_SONG_INFO=$(echo -e "currentsong\nclose" | nc -w 1 localhost 6600)
    CURRENT_SONG_FILE=$(echo "$CURRENT_SONG_INFO" | grep -o -P '(?<=file: ).*')
    CURRENT_SONG_FILE_ABS="${AUDIO_FOLDERS_PATH}/${CURRENT_SONG_FILE}"
    log "current file: $CURRENT_SONG_FILE_ABS"

    CURRENT_SONG_DIR="$(dirname -- "$CURRENT_SONG_FILE_ABS")"
    CURRENT_SONG_BASENAME="$(basename -- "${CURRENT_SONG_FILE_ABS}")"
    CURRENT_SONG_FILE_EXT="${CURRENT_SONG_BASENAME##*.}"
    CURRENT_SONG_ELAPSED=$(echo -e "status\nclose" | nc -w 1 localhost 6600 | grep -o -P '(?<=elapsed: ).*')
    CURRENT_SONG_DURATION=$(echo -e "status\nclose" | nc -w 1 localhost 6600 | grep -o -P '(?<=duration: ).*')

    CHAPTERS_FILE="${CURRENT_SONG_DIR}/${CURRENT_SONG_BASENAME%.*}.chapters.json"
    log "chapters file: $CHAPTERS_FILE"

    if [ "$(grep -wo "$CURRENT_SONG_FILE_EXT" <<< "$CHAPTEREXTENSIONS")" == "$CURRENT_SONG_FILE_EXT" ]; then
        CHAPTER_SUPPORT_FOR_EXTENSION="1"
    else
        CHAPTER_SUPPORT_FOR_EXTENSION="0"
    fi
    log "chapters for extension enabled: $CHAPTER_SUPPORT_FOR_EXTENSION"


    if [ "$(printf "${CURRENT_SONG_DURATION}\n${CHAPTERMINDURATION}\n" | sort -g | head -1)" == "${CHAPTERMINDURATION}" ]; then
        CHAPTER_SUPPORT_FOR_DURATION="1"
    else
        CHAPTER_SUPPORT_FOR_DURATION="0"
    fi
    log "chapters for duration enabled: $CHAPTER_SUPPORT_FOR_DURATION"

    if [ "${CHAPTER_SUPPORT_FOR_EXTENSION}${CHAPTER_SUPPORT_FOR_DURATION}" == "11" ]; then
        if ! [ -f "${CHAPTERS_FILE}" ]; then
            CHAPTERS_COUNT="0"
            log "chaptes file does not exist - export triggered"
            ffprobe -i "${CURRENT_SONG_FILE_ABS}" -print_format json -show_chapters -loglevel error > "${CHAPTERS_FILE}" &
        else
            CHAPTERS_COUNT="$(grep  '"id":' "${CHAPTERS_FILE}" | wc -l )"
            log "chapters file does exist, chapter count: $CHAPTERS_COUNT"
        fi

        CHAPTER_START_TIMES="$( ( echo -e $CURRENT_SONG_ELAPSED & grep 'start_time' "$CHAPTERS_FILE" | cut -d '"' -f 4 | sed 's/000$//') | sort -V)"
        ELAPSED_MATCH_CHAPTER_COUNT=$(grep "$CURRENT_SONG_ELAPSED" <<< "$CHAPTER_START_TIMES" | wc -l)

        # elapsed and chapter start exactly match -> skip one line
        if [ "$ELAPSED_MATCH_CHAPTER_COUNT" == "2" ]; then
            PREV_CHAPTER_START=$(grep "$CURRENT_SONG_ELAPSED" -B 1 <<< "$CHAPTER_START_TIMES" | head -n1)
            CURRENT_CHAPTER_START="$CURRENT_SONG_ELAPSED"
        else
            PREV_CHAPTER_START=$(grep "$CURRENT_SONG_ELAPSED" -B 2 <<< "$CHAPTER_START_TIMES" | head -n1)
            CURRENT_CHAPTER_START=$(grep "$CURRENT_SONG_ELAPSED" -B 1 <<< "$CHAPTER_START_TIMES" | head -n1)
        fi

        NEXT_CHAPTER_START=$(grep "$CURRENT_SONG_ELAPSED" -A 1 <<< "$CHAPTER_START_TIMES" | tail -n1)
    fi
fi # END COMMANDS SHORTCUT

log "   ${COMMAND}"

case $COMMAND in
    shutdown)
        while :
        do
            apt=1
            sudo lsof /var/lib/apt/lists/lock > /dev/null
            apt=$(($apt * $?))
            sudo lsof /var/lib/dpkg/lock > /dev/null
            apt=$(($apt * $?))
            sudo lsof /var/cache/apt/archives/lock > /dev/null
            apt=$(($apt * $?))
            if [ $apt -eq 0 ]; then
                sleep 5
            else
                break
            fi
        done
        ${PATHDATA}/resume_play.sh -c=savepos && mpc clear
        utils_shuffle_mode_off
        sleep 1
        /usr/bin/mpg123 ${PATHDATA}/../shared/shutdownsound.mp3
        sleep 3
        ${POWEROFFCMD}
        ;;
    shutdownsilent)
        # doesn't play a shutdown sound
        while :
        do
            apt=1
            sudo lsof /var/lib/apt/lists/lock > /dev/null
            apt=$(($apt * $?))
            sudo lsof /var/lib/dpkg/lock > /dev/null
            apt=$(($apt * $?))
            sudo lsof /var/cache/apt/archives/lock > /dev/null
            apt=$(($apt * $?))
            if [ $apt -eq 0 ]; then
                sleep 5
            else
                break
            fi
        done
        ${PATHDATA}/resume_play.sh -c=savepos && mpc clear
        utils_shuffle_mode_off
        ${POWEROFFCMD}
        ;;
    shutdownafter)
        # remove shutdown times if existent
        for i in `sudo atq -q t | awk '{print $1}'`;do sudo atrm $i;done
        # -c=shutdownafter -v=0 is to remove the shutdown timer
        if [ ${VALUE} -gt 0 ];
        then
            # shutdown pi after ${VALUE} minutes
            echo "${PATHDATA}/playout_controls.sh -c=shutdownsilent" | at -q t now + ${VALUE} minute
        fi
        ;;
	shutdownvolumereduction)
        # remove existing volume and shutdown commands
		for i in `sudo atq -q r | awk '{print $1}'`;do sudo atrm $i;done
		for i in `sudo atq -q q | awk '{print $1}'`;do sudo atrm $i;done
		# get current volume in percent
		VOLPERCENT=$(echo -e status\\nclose | nc -w 1 localhost 6600 | grep -o -P '(?<=volume: ).*')
		# divide current volume by 10 to get a step size for reducing the volume
		VOLSTEP=`expr $((VOLPERCENT / 10))`;
		# divide VALUE by 10, volume will be reduced every TIMESTEP minutes (e.g. for a value of "30" it will be every "3" minutes)
		TIMESTEP=`expr $((VALUE / 10))`;
		# loop 10 times to reduce the volume by VOLSTEP every TIMESTEP minutes
		for i in $(seq 1 10); do
			VOLPERCENT=`expr ${VOLPERCENT} - ${VOLSTEP}`; echo "${PATHDATA}/playout_controls.sh -c=setvolume -v="$VOLPERCENT | at -q r now + `expr $(((i * TIMESTEP)-1))` minute;
		done
		# schedule shutdown after VALUE minutes
        if [ ${VALUE} -gt 0 ];
        then
			# schedule shutdown after VALUE minutes
			echo "${PATHDATA}/playout_controls.sh -c=shutdownsilent" | at -q q now + ${VALUE} minute
		fi
		;;			
    reboot)
        ${PATHDATA}/resume_play.sh -c=savepos && mpc clear
        utils_shuffle_mode_off
        sudo reboot
        ;;
    scan)
        ${PATHDATA}/resume_play.sh -c=savepos && mpc clear
        utils_shuffle_mode_off
        sudo systemctl stop mopidy
        sudo mopidyctl local scan
        sudo systemctl start mopidy
        ;;
    mute)
        log "   VOLUMEMANAGER: ${VOLUMEMANAGER}"
        if [ ! -f $VOLFILE ]; then
            # $VOLFILE does NOT exist == audio on
            # read volume in percent and write to $VOLFILE
            if [ "${VOLUMEMANAGER}" == "amixer" ]; then
                # volume handling alternative with amixer not mpd (2020-06-12 related to ticket #973)
                amixer sget \'$AUDIOIFACENAME\' | grep -Po -m 1 '(?<=\[)[^]]*(?=%])' > $VOLFILE
            else
                # manage volume with mpd
                echo -e status\\nclose | nc -w 1 localhost 6600 | grep -o -P '(?<=volume: ).*' > $VOLFILE
            fi
            # set volume to 0%
            if [ "${VOLUMEMANAGER}" == "amixer" ]; then
                # volume handling alternative with amixer not mpd (2020-06-12 related to ticket #973)
                amixer sset \'$AUDIOIFACENAME\' 0%
            else
                # manage volume with mpd
                echo -e setvol 0\\nclose | nc -w 1 localhost 6600
            fi
        else
            # $VOLFILE DOES exist == audio off
            # read volume level from $VOLFILE and set as percent
            if [ "${VOLUMEMANAGER}" == "amixer" ]; then
                # volume handling alternative with amixer not mpd (2020-06-12 related to ticket #973)
                amixer sset \'$AUDIOIFACENAME\' `<$VOLFILE`%
            else
                # manage volume with mpd
                echo -e setvol `<$VOLFILE`\\nclose | nc -w 1 localhost 6600
            fi
            # delete $VOLFILE
            rm -f $VOLFILE
        fi
        ;;
    setvolume)
        log "   VOLUMEMANAGER: ${VOLUMEMANAGER}"
        #increase volume only if VOLPERCENT is below the max volume limit and above min volume limit
        if [ ${VALUE} -le $AUDIOVOLMAXLIMIT ] && [ ${VALUE} -ge $AUDIOVOLMINLIMIT ];
        then
            # set volume level in percent
            if [ "${VOLUMEMANAGER}" == "amixer" ]; then
                # volume handling alternative with amixer not mpd (2020-06-12 related to ticket #973)
                amixer sset \'$AUDIOIFACENAME\' $VALUE%
            else
                # manage volume with mpd
                echo -e setvol $VALUE\\nclose | nc -w 1 localhost 6600
            fi
        else
            if [ ${VALUE} -gt $AUDIOVOLMAXLIMIT ];
            then
                # if we are over the max volume limit, set the volume to maxvol
                if [ "${VOLUMEMANAGER}" == "amixer" ]; then
                    # volume handling alternative with amixer not mpd (2020-06-12 related to ticket #973)
                    amixer sset \'$AUDIOIFACENAME\' $AUDIOVOLMAXLIMIT%
                else
                    # manage volume with mpd
                    echo -e setvol $AUDIOVOLMAXLIMIT\\nclose | nc -w 1 localhost 6600
                fi
            fi
            if [ ${VALUE} -lt $AUDIOVOLMINLIMIT ];
            then
                # if we are unter the min volume limit, set the volume to minvol
                if [ "${VOLUMEMANAGER}" == "amixer" ]; then
                    # volume handling alternative with amixer not mpd (2020-06-12 related to ticket #973)
                    amixer sset \'$AUDIOIFACENAME\' $AUDIOVOLMINLIMIT%
                else
                    # manage volume with mpd
                    echo -e setvol $AUDIOVOLMINLIMIT\\nclose | nc -w 1 localhost 6600
                fi
            fi
        fi
        ;;
    volumeup)
        #check for volume change during idle
        if [ $VOLCHANGEIDLE == "FALSE" ] || [ $VOLCHANGEIDLE == "OnlyDown" ];
        then
            PLAYSTATE=$(echo -e "status\nclose" | nc -w 1 localhost 6600 | grep -o -P '(?<=state: ).*')
            if [ "$PLAYSTATE" != "play" ]
            then
                #Volume change is not allowed - leave program
                exit 1
            fi
        fi
        if [ ! -f $VOLFILE ]; then
            if [ -z ${VALUE} ]; then
                VALUE=1
            fi
            # $VOLFILE does NOT exist == audio on
            # read volume in percent
            if [ "${VOLUMEMANAGER}" == "amixer" ]; then
                # volume handling alternative with amixer not mpd (2020-06-12 related to ticket #973)
                VOLPERCENT=`amixer sget \'$AUDIOIFACENAME\' | grep -Po -m 1 '(?<=\[)[^]]*(?=%])'`
            else
                # manage volume with mpd
                VOLPERCENT=$(echo -e status\\nclose | nc -w 1 localhost 6600 | grep -o -P '(?<=volume: ).*')
            fi
            # increase by $AUDIOVOLCHANGESTEP
            VOLPERCENT=`expr ${VOLPERCENT} + \( ${AUDIOVOLCHANGESTEP} \* ${VALUE} \)`
            log "   VOLPERCENT:${VOLPERCENT} | VOLUMEMANAGER:${VOLUMEMANAGER}"
            #increase volume only if VOLPERCENT is below the max volume limit
            if [ $VOLPERCENT -le $AUDIOVOLMAXLIMIT ];
            then
                # set volume level in percent
                if [ "${VOLUMEMANAGER}" == "amixer" ]; then
                    # volume handling alternative with amixer not mpd (2020-06-12 related to ticket #973)
                    amixer sset \'$AUDIOIFACENAME\' ${VOLPERCENT}%
                else
                    # manage volume with mpd
                    echo -e setvol +$VOLPERCENT\\nclose | nc -w 1 localhost 6600
                fi
            else
                # if we are over the max volume limit, set the volume to maxvol
                if [ "${VOLUMEMANAGER}" == "amixer" ]; then
                    # volume handling alternative with amixer not mpd (2020-06-12 related to ticket #973)
                    amixer sset \'$AUDIOIFACENAME\' ${AUDIOVOLMAXLIMIT}%
                else
                    # manage volume with mpd
                    echo -e setvol $AUDIOVOLMAXLIMIT\\nclose | nc -w 1 localhost 6600
                fi
            fi
        else
            # $VOLFILE DOES exist == audio off
            # read volume level from $VOLFILE and set as percent
            if [ "${VOLUMEMANAGER}" == "amixer" ]; then
                # volume handling alternative with amixer not mpd (2020-06-12 related to ticket #973)
                amixer sset \'$AUDIOIFACENAME\' `<$VOLFILE`%
            else
                # manage volume with mpd
                echo -e setvol `<$VOLFILE`\\nclose | nc -w 1 localhost 6600
            fi
            # delete $VOLFILE
            rm -f $VOLFILE
        fi
        ;;
    volumedown)
        #check for volume change during idle
        if [ $VOLCHANGEIDLE == "FALSE" ] || [ $VOLCHANGEIDLE == "OnlyUp" ];
        then
            PLAYSTATE=$(echo -e "status\nclose" | nc -w 1 localhost 6600 | grep -o -P '(?<=state: ).*')
            if [ "$PLAYSTATE" != "play" ]
            then
                #Volume change is not allowed - leave program
                exit 1
            fi
        fi
        if [ ! -f $VOLFILE ]; then
            if [ -z ${VALUE} ]; then
                VALUE=1
            fi
            # $VOLFILE does NOT exist == audio on
            # read volume in percent
            if [ "${VOLUMEMANAGER}" == "amixer" ]; then
                # volume handling alternative with amixer not mpd (2020-06-12 related to ticket #973)
                VOLPERCENT=`amixer sget \'$AUDIOIFACENAME\' | grep -Po -m 1 '(?<=\[)[^]]*(?=%])'`
            else
                # manage volume with mpd
                VOLPERCENT=$(echo -e status\\nclose | nc -w 1 localhost 6600 | grep -o -P '(?<=volume: ).*')
            fi
            # decrease by $AUDIOVOLCHANGESTEP
            VOLPERCENT=`expr ${VOLPERCENT} - \( ${AUDIOVOLCHANGESTEP} \* ${VALUE} \)`
            log "   VOLPERCENT:${VOLPERCENT} | VOLUMEMANAGER:${VOLUMEMANAGER}"
            #decrease volume only if VOLPERCENT is above the min volume limit
            if [ $VOLPERCENT -ge $AUDIOVOLMINLIMIT ];
            then
                # set volume level in percent
                if [ "${VOLUMEMANAGER}" == "amixer" ]; then
                    # volume handling alternative with amixer not mpd (2020-06-12 related to ticket #973)
                    amixer sset \'$AUDIOIFACENAME\' ${VOLPERCENT}%
                else
                    # manage volume with mpd
                    echo -e setvol +$VOLPERCENT\\nclose | nc -w 1 localhost 6600
                fi
            else
                # if we are below the min volume limit, set the volume to minvol
                if [ "${VOLUMEMANAGER}" == "amixer" ]; then
                    # volume handling alternative with amixer not mpd (2020-06-12 related to ticket #973)
                    amixer sset \'$AUDIOIFACENAME\' ${AUDIOVOLMINLIMIT}%
                else
                    # manage volume with mpd
                    echo -e setvol $AUDIOVOLMINLIMIT\\nclose | nc -w 1 localhost 6600
                fi
            fi
        else
            # $VOLFILE DOES exist == audio off
            # read volume level from $VOLFILE and set as percent
            if [ "${VOLUMEMANAGER}" == "amixer" ]; then
                # volume handling alternative with amixer not mpd (2020-06-12 related to ticket #973)
                amixer sset \'$AUDIOIFACENAME\' `<$VOLFILE`%
            else
                # manage volume with mpd
                echo -e setvol `<$VOLFILE`\\nclose | nc -w 1 localhost 6600
            fi
            # delete $VOLFILE
            rm -f $VOLFILE
        fi
        ;;
    getchapters)
        if [ -f "${CHAPTERS_FILE}" ]; then cat "${CHAPTERS_FILE}"; fi
        ;;
    getvolume)
        # read volume in percent
        log "#  ${COMMAND}"
        if [ "${VOLUMEMANAGER}" == "amixer" ]; then
            # volume handling alternative with amixer not mpd (2020-06-12 related to ticket #973)
            VOLPERCENT=`amixer sget \'$AUDIOIFACENAME\' | grep -Po -m 1 '(?<=\[)[^]]*(?=%])'`
        else
            # manage volume with mpd
            VOLPERCENT=$(echo -e status\\nclose | nc -w 1 localhost 6600 | grep -o -P '(?<=volume: ).*')
        fi
        log "   VOLPERCENT:${VOLPERCENT} | VOLUMEMANAGER:${VOLUMEMANAGER}"
        echo $VOLPERCENT
        ;;
    setmaxvolume)
        # read volume in percent
        if [ "${VOLUMEMANAGER}" == "amixer" ]; then
            # volume handling alternative with amixer not mpd (2020-06-12 related to ticket #973)
            VOLPERCENT=`amixer sget \'$AUDIOIFACENAME\' | grep -Po -m 1 '(?<=\[)[^]]*(?=%])'`
        else
            # manage volume with mpd
            VOLPERCENT=$(echo -e status\\nclose | nc -w 1 localhost 6600 | grep -o -P '(?<=volume: ).*')
        fi
        # if volume of the box is greater than wanted maxvolume, set volume to maxvolume
        if [ $VOLPERCENT -gt ${VALUE} ];
        then
            if [ "${VOLUMEMANAGER}" == "amixer" ]; then
                # volume handling alternative with amixer not mpd (2020-06-12 related to ticket #973)
                amixer sset \'$AUDIOIFACENAME\' ${VALUE}%
            else
                # manage volume with mpd
                echo -e setvol ${VALUE} | nc -w 1 localhost 6600
            fi
        fi
        # if startupvolume is greater than wanted maxvolume, set startupvolume to maxvolume
        if [ ${AUDIOVOLSTARTUP} -gt ${VALUE} ];
        then
            # write new value to file
            echo "$VALUE" > ${PATHDATA}/../settings/Startup_Volume
        fi
        # write new value to file
        echo "$VALUE" > ${PATHDATA}/../settings/Max_Volume_Limit
        # create global config file because individual setting got changed
        . ${PATHDATA}/inc.writeGlobalConfig.sh
        ;;
    getmaxvolume)
        echo $AUDIOVOLMAXLIMIT
        ;;
    setvolstep)
        # write new value to file
        echo "$VALUE" > ${PATHDATA}/../settings/Audio_Volume_Change_Step
        # create global config file because individual setting got changed
        . ${PATHDATA}/inc.writeGlobalConfig.sh
        ;;
    getvolstep)
        echo $AUDIOVOLCHANGESTEP
        ;;
    setstartupvolume)
        # if value is greater than wanted maxvolume, set value to maxvolume
        if [ ${VALUE} -gt $AUDIOVOLMAXLIMIT ];
        then
            VALUE=$AUDIOVOLMAXLIMIT;
        fi
        # write new value to file
        echo "$VALUE" > ${PATHDATA}/../settings/Startup_Volume
        # create global config file because individual setting got changed
        . ${PATHDATA}/inc.writeGlobalConfig.sh
        ;;
    getstartupvolume)
        echo ${AUDIOVOLSTARTUP}
        ;;
    setvolumetostartup)
        # check if startup-volume is disabled
        if [ "${AUDIOVOLSTARTUP}" == 0 ]; then
            exit 1
        else
            # set volume level in percent
            if [ "${VOLUMEMANAGER}" == "amixer" ]; then
                # volume handling alternative with amixer not mpd (2020-06-12 related to ticket #973)
                amixer sset \'$AUDIOIFACENAME\' ${AUDIOVOLSTARTUP}%
            else
                # manage volume with mpd
                echo -e setvol ${AUDIOVOLSTARTUP}\\nclose | nc -w 1 localhost 6600
            fi

        fi
        ;;
    playerstop)
        # stop the player
        ${PATHDATA}/resume_play.sh -c=savepos && mpc stop
        #if [ -e $AUDIOFOLDERSPATH/playing.txt ]
        #then
        #    sudo rm $AUDIOFOLDERSPATH/playing.txt
        #fi
        log "remove playing.txt"
        ;;
    playerstopafter)
        # remove playerstop timer if existent
        for i in `sudo atq -q s | awk '{print $1}'`;do sudo atrm $i;done
        # stop player after ${VALUE} minutes
        if [ ${VALUE} -gt 0 ];
        then
            echo "${PATHDATA}/resume_play.sh -c=savepos && mpc stop" | at -q s now + ${VALUE} minute
        fi
        ;;
    playernext)
        # play next track in playlist (==folder)
        # Unmute if muted
        if [ -f $VOLFILE ]; then
            # $VOLFILE DOES exist == audio off
            # read volume level from $VOLFILE and set as percent
            echo -e setvol `<$VOLFILE`\\nclose | nc -w 1 localhost 6600
            # volume handling alternative with amixer not mpd (2020-06-12 related to ticket #973)
            # amixer sset \'$AUDIOIFACENAME\' `<$VOLFILE`%
            # delete $VOLFILE
            rm -f $VOLFILE
        fi

        mpc next
        ;;
    playerprev)
        # play previous track in playlist (==folder)
        # Unmute if muted
        if [ -f $VOLFILE ]; then
            # $VOLFILE DOES exist == audio off
            # read volume level from $VOLFILE and set as percent
            echo -e setvol `<$VOLFILE`\\nclose | nc -w 1 localhost 6600
            # volume handling alternative with amixer not mpd (2020-06-12 related to ticket #973)
            # amixer sset \'$AUDIOIFACENAME\' `<$VOLFILE`%
            # delete $VOLFILE
            rm -f $VOLFILE
        fi

        mpc prev
        ;;
    playerprevchapter)
        CURRENT_SONG_ELAPSED_MS=$(sec_to_ms "$CURRENT_SONG_ELAPSED")
        CURRENT_CHAPTER_START_MS=$(sec_to_ms "$CURRENT_CHAPTER_START")
        CHAPTER_DIFF_ELAPSED_CURRENT_MS=$(($CURRENT_SONG_ELAPSED_MS-$CURRENT_CHAPTER_START_MS))

        # if elapsed - current > 5.000 => seek current chapter
        # if elapsed - current <= 5.000 => seek prev chapter
        # if prev === 0.000 && elapsed < 5.000 => prev track? (don't do that)
        if [ "$CHAPTER_DIFF_ELAPSED_CURRENT_MS" -gt 5000 ]; then
          log "chapter is already running for longer, seek to current chapter: $SEEK_POS"
          echo -e "seekcur $CURRENT_CHAPTER_START\nclose" | nc -w 1 localhost 6600
        else
          log "chapter just started, seek to prev chapter $PREV_CHAPTER_START"
          echo -e "seekcur $PREV_CHAPTER_START\nclose" | nc -w 1 localhost 6600
        fi
        ;;
    playernextchapter)
        # if next === elapsed => next track
        if ! [ "$NEXT_CHAPTER_START" == "$CURRENT_SONG_ELAPSED" ]; then
          log "next chapter $NEXT_CHAPTER_START"
          echo -e "seekcur $NEXT_CHAPTER_START\nclose" | nc -w 1 localhost 6600
        else
          log "next chapter not available, last chapter already playing"
        fi
        ;;
    playerrewind)
        # play the first track in playlist (==folder)
        # Unmute if muted
        if [ -f $VOLFILE ]; then
            # $VOLFILE DOES exist == audio off
            # read volume level from $VOLFILE and set as percent
            echo -e setvol `<$VOLFILE`\\nclose | nc -w 1 localhost 6600
            # volume handling alternative with amixer not mpd (2020-06-12 related to ticket #973)
            # amixer sset \'$AUDIOIFACENAME\' `<$VOLFILE`%
            # delete $VOLFILE
            rm -f $VOLFILE
        fi

	      mpc play 1
        ;;
    playerpause)
        # toggle current track
        # mpc knows "pause", which pauses only, and "toggle" which pauses and unpauses, whatever is needed
        # Why on earth has this been called pause instead of toggle? :-)

        # Unmute if muted
        if [ -f $VOLFILE ]; then
            # $VOLFILE DOES exist == audio off
            # read volume level from $VOLFILE and set as percent
            echo -e setvol `<$VOLFILE`\\nclose | nc -w 1 localhost 6600
            # volume handling alternative with amixer not mpd (2020-06-12 related to ticket #973)
            # amixer sset \'$AUDIOIFACENAME\' `<$VOLFILE`%
            # delete $VOLFILE
            rm -f $VOLFILE
        fi
        mpc toggle
        ;;
    playerpauseforce)
        # pause current track with optional delay
        if [ -n ${VALUE} ];
        then
	       /bin/sleep $VALUE
        fi
        mpc pause
        ;;
    playerplay)
        # play / resume current track
        log "Attempting to play: $VALUE"
        # May be called with e.g. -v=1 to start a track in the middle of the playlist.
        # Note: the numbering of the tracks starts with 0, so -v=1 starts the second track
        # of the playlist
        # Another note: "mpc play 1" starts the first track (!)

        # Change some settings according to current folder IF the folder.conf exists
        . ${PATHDATA}/inc.settingsFolderSpecific.sh

        # Unmute if muted
        if [ -f $VOLFILE ]; then
            # $VOLFILE DOES exist == audio off
            # read volume level from $VOLFILE and set as percent
            echo -e setvol `<$VOLFILE`\\nclose | nc -w 1 localhost 6600
            # volume handling alternative with amixer not mpd (2020-06-12 related to ticket #973)
            # amixer sset \'$AUDIOIFACENAME\' `<$VOLFILE`%
            # delete $VOLFILE
            rm -f $VOLFILE
        fi

        # No checking for resume if the audio is paused, just unpause it
        PLAYSTATE=$(echo -e "status\nclose" | nc -w 1 localhost 6600 | grep -o -P '(?<=state: ).*')
        if [ "$PLAYSTATE" == "pause" ]
        then
            echo -e "play $VALUE\nclose" | nc -w 1 localhost 6600
        else
            #${PATHDATA}/resume_play.sh -c=resume -v=$VALUE
            mpc play $VALUE
        fi
        ;;
    playerremove)
        # remove selected song position
        log "Attempting to remove: $VALUE"

        # Change some settings according to current folder IF the folder.conf exists
        . ${PATHDATA}/inc.settingsFolderSpecific.sh

        mpc del $VALUE
        ;;
    playermoveup)
        # remove selected song position
        log "Attempting to move: $VALUE"

        # Change some settings according to current folder IF the folder.conf exists
        . ${PATHDATA}/inc.settingsFolderSpecific.sh

        mpc move $(($VALUE)) $(($VALUE-1))
        ;;
    playermovedown)
        # remove selected song position
        log "Attempting to move: $VALUE"

        # Change some settings according to current folder IF the folder.conf exists
        . ${PATHDATA}/inc.settingsFolderSpecific.sh

        mpc move $(($VALUE)) $(($VALUE+1))
        ;;
    playerseek)
        # jumps back and forward in track.
        # Usage: ./playout_controls.sh -c=playerseek -v=+15 to jump 15 seconds ahead
        #        ./playout_controls.sh -c=playerseek -v=-10 to jump 10 seconds back
        # Note: Not using "mpc seek" here as it fails if one tries to jump ahead of the beginning of the track
        # (e.g. "mpc seek -15" executed at an elapsed time of 10 seconds let the player hang).
        # mpd seekcur can handle this.
        # Unmute if muted
        if [ -f $VOLFILE ]; then
            # $VOLFILE DOES exist == audio off
            # read volume level from $VOLFILE and set as percent
            echo -e setvol `<$VOLFILE`\\nclose | nc -w 1 localhost 6600
            # volume handling alternative with amixer not mpd (2020-06-12 related to ticket #973)
            # amixer sset \'$AUDIOIFACENAME\' `<$VOLFILE`%
            # delete $VOLFILE
            rm -f $VOLFILE
        fi

        # if value does not start with + or - (relative seek), perform an absolute seek
        if [[ $VALUE =~ ^[0-9] ]]; then
          # seek absolute position
          echo -e "seekcur $VALUE\nclose" | nc -w 1 localhost 6600
        else
          # Seek negative value doesn't work in mpd anymore.
          # solution taken from: https://github.com/MiczFlor/RPi-Jukebox-RFID/issues/1031
          # if there are issues, please comment in that thread
          CUR_POS=$(echo -e "status\nclose" | nc -w 1 localhost 6600 | grep -o -P '(?<=elapsed: ).*' | awk '{print int($1)}')
          NEW_POS=$(($CUR_POS + $VALUE))
          echo -e "seekcur $NEW_POS\nclose" | nc -w 1 localhost 6600
        fi
        ;;
    playerreplay)
        # start the playing track from beginning
        # Unmute if muted
        if [ -f $VOLFILE ]; then
            # $VOLFILE DOES exist == audio off
            # read volume level from $VOLFILE and set as percent
            echo -e setvol `<$VOLFILE`\\nclose | nc -w 1 localhost 6600
            # volume handling alternative with amixer not mpd (2020-06-12 related to ticket #973)
            # amixer sset \'$AUDIOIFACENAME\' `<$VOLFILE`%
            # delete $VOLFILE
            rm -f $VOLFILE
        fi
        mpc seek 0
        ;;
    playerrepeat)
        log "   value: ${VALUE}"
        # repeats a single track or a playlist.
        # Remark: If "single" is "on" but "repeat" is "off", the playout stops after the current song.
        # This command may be called with ./playout_controls.sh -c=playerrepeat -v=single, playlist or off

        case ${VALUE} in
            single)
                mpc repeat on
                mpc single on
                ;;
            playlist)
                mpc repeat on
                mpc single off
                ;;
            *)
                mpc repeat off
                mpc single off
                ;;
        esac
        ;;
    playershuffle)
        # toogles shuffle mode on/off (not only the current playlist but for the whole mpd)
        # this is why a check if "random on" has to be done for shutdown and reboot
        # This command may be called with ./playout_controls.sh -c=playershuffle
        mpc shuffle
        ;;
    playlistclear)
        # clear playlist
        ${PATHDATA}/resume_play.sh -c=savepos
        mpc clear
        ;;
    playlistaddplay)
        # add to playlist (and play)
        # this command clears the playlist, loads a new playlist and plays it. It also handles the resume play feature.
        # FOLDER = rel path from audiofolders
        # VALUE = name of playlist
        log "   playlistaddplay playlist name VALUE: $VALUE"
        log "   playlistaddplay FOLDER: $FOLDER"

        # NEW VERSION:
        # Read the current config file (include will execute == read)
        . "$AUDIOFOLDERSPATH/$FOLDER/folder.conf"

        # load playlist
        mpc clear
        mpc load "${VALUE//\//SLASH}"
        log "mpc load "${VALUE//\//SLASH}

        # Change some settings according to current folder IF the folder.conf exists
        #. ${PATHDATA}/inc.settingsFolderSpecific.sh

        # check if we switch to single file playout
        ${PATHDATA}/single_play.sh -c=single_check -d="${FOLDER}"

        # check if we shuffle the playlist
        ${PATHDATA}/shuffle_play.sh -c=shuffle_check -d="${FOLDER}"

        # Unmute if muted
        if [ -f $VOLFILE ]; then
            # $VOLFILE DOES exist == audio off
            # read volume level from $VOLFILE and set as percent
            echo -e setvol `<$VOLFILE`\\nclose | nc -w 1 localhost 6600
            # volume handling alternative with amixer not mpd (2020-06-12 related to ticket #973)
            # amixer sset \'$AUDIOIFACENAME\' `<$VOLFILE`%
            # delete $VOLFILE
            rm -f $VOLFILE
        fi

        # Now load and play
        log "mpc load "${VALUE//\//SLASH}" && ${PATHDATA}/resume_play.sh -c=resume -d="${FOLDER}""
        ${PATHDATA}/resume_play.sh -c=resume -d="${FOLDER}"

        # write latest folder played to settings file
        sudo echo ${FOLDER} > ${PATHDATA}/../settings/Latest_Folder_Played
        sudo chown pi:www-data ${PATHDATA}/../settings/Latest_Folder_Played
        sudo chmod 777 ${PATHDATA}/../settings/Latest_Folder_Played
        log "  echo ${FOLDER} > ${PATHDATA}/../settings/Latest_Folder_Played"
        log "  VAR Latest_Folder_Played: ${FOLDER}"
        log "  # end playout_controls.sh playlistaddplay"

        # OLD VERSION (pre 20190302 - delete once the new version really seems to work):
        # call shuffle_check HERE to enable/disable folder-based shuffling
        # (mpc shuffle is different to random, because when you shuffle before playing,
        # you start your playlist with a different track EVERYTIME. With random you EVER
        # has the first song and random from track 2.
        #mpc load "${VALUE//\//SLASH}" && ${PATHDATA}/shuffle_play.sh -c=shuffle_check && ${PATHDATA}/single_play.sh -c=single_check && ${PATHDATA}/resume_play.sh -c=resume
        #mpc load "${VALUE//\//SLASH}" && ${PATHDATA}/single_play.sh -c=single_check  && ${PATHDATA}/resume_play.sh -c=resume

        ;;
    playlistadd)
        # add to playlist, no autoplay
        log "   value: ${VALUE}"
        # save playlist playing
        mpc load "${VALUE}"
        ;;
    playlistappend)
        log "   value: ${VALUE}"
        mpc add "${VALUE}"
        # Unmute if muted
        if [ -f $VOLFILE ]; then
            # $VOLFILE DOES exist == audio off
            # read volume level from $VOLFILE and set as percent
            echo -e setvol `<$VOLFILE`\\nclose | nc -w 1 localhost 6600
            # delete $VOLFILE
            rm -f $VOLFILE
        fi
        mpc play
        ;;
     playlistreset)
        if [ -e $PATHDATA/../shared/audiofolders/$FOLDERPATH/lastplayed.dat ]
        then
           echo "" > $PATHDATA/../shared/audiofolders/$FOLDERPATH/lastplayed.dat
        fi
        mpc play 1
        ;;
    playsinglefile)
        log "   value: ${VALUE}"
        mpc clear
        mpc add "${VALUE}"
        mpc repeat off
        mpc single on
        # Unmute if muted
        if [ -f $VOLFILE ]; then
            # $VOLFILE DOES exist == audio off
            # read volume level from $VOLFILE and set as percent
            echo -e setvol `<$VOLFILE`\\nclose | nc -w 1 localhost 6600
            # delete $VOLFILE
            rm -f $VOLFILE
        fi
        mpc play
        ;;
    setidletime)
        log "   value: ${VALUE}"
        # write new value to file
        echo "$VALUE" > ${PATHDATA}/../settings/Idle_Time_Before_Shutdown
        # create global config file because individual setting got changed
        . ${PATHDATA}/inc.writeGlobalConfig.sh
        # restart service to apply the new value
        sudo systemctl restart phoniebox-idle-watchdog.service &
        ;;
    getidletime)
        echo $IDLETIMESHUTDOWN
        ;;
    enablewifi)
        rfkill unblock wifi
        ;;
    disablewifi)
        # see https://forum-raspberrypi.de/forum/thread/25696-bluetooth-und-wlan-deaktivieren/#pid226072 seems to disable wifi,
        # as good as it gets
        rfkill block wifi
        ;;
    togglewifi)
        # function to allow toggle the wifi state
        # Build special for franzformator
        rfkill list wifi | grep -i "Soft blocked: no" > /dev/null 2>&1
        WIFI_SOFTBLOCK_RESULT=$?
        wpa_cli -i wlan0 status | grep 'ip_address' > /dev/null 2>&1
        WIFI_IP_RESULT=$?
        log "   WIFI_IP_RESULT='${WIFI_IP_RESULT}' WIFI_SOFTBLOCK_RESULT='${WIFI_SOFTBLOCK_RESULT}'"
        if [ $WIFI_SOFTBLOCK_RESULT -eq 0 ] && [ $WIFI_IP_RESULT -eq 0 ]
        then
            log "   Wifi will now be deactivated"
            echo "Wifi will now be deactivated"
            rfkill block wifi
        else
            log "   Wifi will now be activated"
            echo "Wifi will now be activated"
            rfkill unblock wifi
        fi
        ;;
    recordstart)
        #mkdir $AUDIOFOLDERSPATH/Recordings
        #kill the potential current playback
        sudo pkill aplay
        #start recorder if not already started
        if ! pgrep -x "arecord" > /dev/null
        then
            echo "start recorder"
            arecord -D plughw:1 --duration=${VALUE} -f cd -vv $AUDIOFOLDERSPATH/Recordings/$(date +"%Y-%m-%d_%H-%M-%S").wav &
        else
            echo "device is already recording"
        fi
        ;;
    recordstop)
        #kill arecord instances
        sudo pkill arecord
        ;;
        recordplaylatest)
        #kill arecord and aplay instances
        sudo pkill arecord
        sudo pkill aplay
        # Unmute if muted
        if [ -f $VOLFILE ]; then
            # $VOLFILE DOES exist == audio off
            # read volume level from $VOLFILE and set as percent
            echo -e setvol `<$VOLFILE`\\nclose | nc -w 1 localhost 6600
            # delete $VOLFILE
            rm -f $VOLFILE
        fi
        aplay `ls $AUDIOFOLDERSPATH/Recordings/*.wav -1t|head -1`
        ;;
    readwifiipoverspeaker)
        # will read out the IP address over the Pi's speaker.
        # Why? Imagine to go to a new wifi, hook up and not know where to point your browser
        cd /home/pi/RPi-Jukebox-RFID/misc/
        # delete older mp3 (in case process was interrupted)
        sudo rm WifiIp.mp3
        /usr/bin/php /home/pi/RPi-Jukebox-RFID/scripts/helperscripts/cli_ReadWifiIp.php
        ;;
    bluetoothtoggle)
        if [ "${DEBUG_playout_controls_sh}" == "TRUE" ]; then echo "   ${COMMAND}" >> ${PATHDATA}/../logs/debug.log; fi
        $PATHDATA/../components/bluetooth-sink-switch/bt-sink-switch.py $VALUE
        ;;
    switchaudioiface)
        # will switch between primary/secondary audio iFace (e.g. speaker/headphones), if exist
        dbg "   ${COMMAND}"
        if [ "${VOLUMEMANAGER}" == "amixer" ]; then
            NEXTAUDIOIFACE=$(((${AUDIOIFACEACTIVE}+1) % 2))
            if [ -f ${IFACEFILE}_${NEXTAUDIOIFACE} ]; then
                NEXTAUDIOIFACENAME=`<${IFACEFILE}_${NEXTAUDIOIFACE}`
                if [ -f ${VOLFILE}_${NEXTAUDIOIFACE} ]; then
                    NEXTAUDIOIFACEVOL=`<${VOLFILE}_${NEXTAUDIOIFACE}`
                else
                    NEXTAUDIOIFACEVOL=${AUDIOVOLMAXLIMIT}
                fi
                # store current volume
                amixer sget \'${AUDIOIFACENAME}\' | grep -Po -m 1 '(?<=\[)[^]]*(?=%])' > ${VOLFILE}_${AUDIOIFACEACTIVE}
                # unmute next audio iFace
                amixer sset \'${NEXTAUDIOIFACENAME}\' ${NEXTAUDIOIFACEVOL}%
                # mute current audio iFace
                amixer sset \'${AUDIOIFACENAME}\' 0%
                # store new active audio iFace
                cp ${IFACEFILE}_${NEXTAUDIOIFACE} ${IFACEFILE}
                echo "${NEXTAUDIOIFACE}" > ${PATHDATA}/../settings/Audio_iFace_Active
                # create global config file because individual setting got changed (time consuming)
                . ${PATHDATA}/inc.writeGlobalConfig.sh
            else
                dbg "Cannot switch audio iFace. ${IFACEFILE}_${NEXTAUDIOIFACE} does not exist."
            fi
        else
            dbg "Command requires \"amixer\" as volume manager."
        fi
        ;;
    *)
        echo Unknown COMMAND $COMMAND VALUE $VALUE
        log "Unknown COMMAND ${COMMAND} VALUE ${VALUE}"
        ;;
esac
