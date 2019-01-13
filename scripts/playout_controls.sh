#!/bin/bash

# This shell script contains all the functionality to control
# playout and change volume and the like.
# This script is called from the web app and the bash script.
# The purpose is to have all playout logic in one place, this
# makes further development and potential replacement of 
# the playout player easier.

# $DEBUG true|false
# prints $COMMAND in the terminal and/or log file
DEBUG=false

# Set the date and time of now
NOW=`date +%Y-%m-%d.%H:%M:%S`

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
# reboot
# scan
# mute
# setvolume
# setmaxvolume
# volumeup
# volumedown
# getvolume
# getmaxvolume
# setvolstep
# getvolstep
# playerstop
# playerstopafter
# playernext
# playerprev
# playerpause
# playerplay
# playerreplay
# playerrepeat
# playershuffle
# playlistclear
# playlistaddplay
# playlistadd
# getidletime
# setidletime
# disablewifi
# enablewifi
# togglewifi
# recordstart
# recordstop
# recordplaylatest

# SET VARIABLES
# The variables can be changed in the ../settings dir.
# Relevant files are:
# * ../settings/Audio_Volume_Change_Step
# * ../settings/Audio_iFace_Name

# The absolute path to the folder whjch contains all the scripts.
# Unless you are working with symlinks, leave the following line untouched.
PATHDATA="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
if [ "$DEBUG" == "true" ]; then echo "########### SCRIPT playout_controls.sh ($NOW) ##" >> $PATHDATA/../logs/debug.log; fi

##############################################
# steps by which to change the audio output (vol up and down)
# 1. create a default if file does not exist
if [ ! -f $PATHDATA/../settings/Audio_Volume_Change_Step ]; then
    echo "3" > $PATHDATA/../settings/Audio_Volume_Change_Step
fi
# 2. then|or read value from file
VOLSTEP=`cat $PATHDATA/../settings/Audio_Volume_Change_Step`

##############################################
# Max volume limit
# 1. create a default if file does not exist
if [ ! -f $PATHDATA/../settings/Max_Volume_Limit ]; then
    echo "100" > $PATHDATA/../settings/Max_Volume_Limit
fi
# 2. then|or read value from file
MAXVOL=`cat $PATHDATA/../settings/Max_Volume_Limit`

MINVOL='1'

#################################
# path to file storing the current volume level
# this file does not need to exist
# it will be created or deleted by this script
VOLFILE=$PATHDATA/../settings/Audio_Volume_Level

#################################
# Idle time after the RPi will be shut down. 0=turn off feature.
# 1. create a default if file does not exist
if [ ! -f $PATHDATA/../settings/Idle_Time_Before_Shutdown ]; then
    echo "0" > $PATHDATA/../settings/Idle_Time_Before_Shutdown
fi
# 2. then|or read value from file
IDLETIME=`cat $PATHDATA/../settings/Idle_Time_Before_Shutdown`

##############################################
# Path to folder containing audio / streams
# 1. create a default if file does not exist
if [ ! -f $PATHDATA/../settings/Audio_Folders_Path ]; then
    echo "/home/pi/RPi-Jukebox-RFID/shared/audiofolders" > $PATHDATA/../settings/Audio_Folders_Path
fi
# 2. then|or read value from file
AUDIOFOLDERSPATH=`cat $PATHDATA/../settings/Audio_Folders_Path`

#echo $VOLSTEP
#echo $VOLFILE
#echo $MAXVOL
#echo `cat $VOLFILE`
#echo $IDLETIME
#echo $AUDIOFOLDERSPATH

#############################################################

# Get args from command line (see Usage above)
# Read the args passed on by the command line
# see following file for details:
. $PATHDATA/inc.readArgsFromCommandLine.sh
#for i in "$@"
#do
#    case $i in
#        -c=*|--command=*)
#        COMMAND="${i#*=}"
#        ;;
#        -v=*|--value=*)
#        VALUE="${i#*=}"
#        ;;
#    esac
#done

if [ "$DEBUG" == "true" ]; then echo "VAR COMMAND: $COMMAND" >> $PATHDATA/../logs/debug.log; fi
if [ "$DEBUG" == "true" ]; then echo "VAR VALUE: $VALUE" >> $PATHDATA/../logs/debug.log; fi
        
case $COMMAND in 
    shutdown)
        if [ "$DEBUG" == "true" ]; then echo "   shutdown" >> $PATHDATA/../logs/debug.log; fi
        $PATHDATA/resume_play.sh -c=savepos && mpc clear
    	#remove shuffle mode if active
        SHUFFLE_STATUS=$(echo -e status\\nclose | nc -w 1 localhost 6600 | grep -o -P '(?<=random: ).*')
        if [ "$SHUFFLE_STATUS" == 1 ] ; then  mpc random off; fi
        sleep 1
        /usr/bin/mpg123 $PATHDATA/../shared/shutdownsound.mp3 
        sleep 3
        sudo poweroff
        ;;
    shutdownsilent)
        # doesn't play a shutdown sound
        $PATHDATA/resume_play.sh -c=savepos && mpc clear
        #remove shuffle mode if active
        SHUFFLE_STATUS=$(echo -e status\\nclose | nc -w 1 localhost 6600 | grep -o -P '(?<=random: ).*')
        if [ "$SHUFFLE_STATUS" == 1 ] ; then  mpc random off; fi
	sudo poweroff
        ;;
    shutdownafter)
        # remove shutdown times if existent
        for i in `sudo atq -q t | awk '{print $1}'`;do sudo atrm $i;done
        # -c=shutdownafter -v=0 is to remove the shutdown timer
        if [ $VALUE -gt 0 ];
        then
            # shutdown pi after $VALUE minutes
            echo "$PATHDATA/playout_controls.sh -c=shutdownsilent" | at -q t now + $VALUE minute
        fi 
        ;;
    reboot)
        $PATHDATA/resume_play.sh -c=savepos && mpc clear
        #remove shuffle mode if active
        SHUFFLE_STATUS=$(echo -e status\\nclose | nc -w 1 localhost 6600 | grep -o -P '(?<=random: ).*')
        if [ "$SHUFFLE_STATUS" == 1 ] ; then  mpc random off; fi
        sudo reboot
        ;;
    scan)
        $PATHDATA/resume_play.sh -c=savepos && mpc clear
        #remove shuffle mode if active
        SHUFFLE_STATUS=$(echo -e status\\nclose | nc -w 1 localhost 6600 | grep -o -P '(?<=random: ).*')
        if [ "$SHUFFLE_STATUS" == 1 ] ; then  mpc random off; fi
        sudo systemctl stop mopidy
		sudo mopidyctl local scan
		sudo systemctl start mopidy
        ;;
    mute)
        if [ ! -f $VOLFILE ]; then
            # $VOLFILE does NOT exist == audio on
            # read volume in percent and write to $VOLFILE
            echo -e status\\nclose | nc -w 1 localhost 6600 | grep -o -P '(?<=volume: ).*' > $VOLFILE
            # set volume to 0%
            echo -e setvol 0\\nclose | nc -w 1 localhost 6600
        else
            # $VOLFILE DOES exist == audio off
            # read volume level from $VOLFILE and set as percent
            echo -e setvol `<$VOLFILE`\\nclose | nc -w 1 localhost 6600        
            # delete $VOLFILE
            rm -f $VOLFILE
        fi
        ;;
    setvolume)
        #increase volume only if VOLPERCENT is below the max volume limit
        if [ $VALUE -le $MAXVOL ];
        then
            # set volume level in percent
            echo -e setvol $VALUE\\nclose | nc -w 1 localhost 6600
        else
            # if we are over the max volume limit, set the volume to maxvol
            echo -e setvol $MAXVOL\\nclose | nc -w 1 localhost 6600
        fi
        ;;
    volumeup)
        if [ ! -f $VOLFILE ]; then
            if [ -z $VALUE ]; then
		VALUE=1
	    fi
            # $VOLFILE does NOT exist == audio on
            # read volume in percent
            VOLPERCENT=$(echo -e status\\nclose | nc -w 1 localhost 6600 | grep -o -P '(?<=volume: ).*')
            # increase by $VOLSTEP
            VOLPERCENT=`expr ${VOLPERCENT} + \( ${VOLSTEP} \* ${VALUE} \)` 
            #increase volume only if VOLPERCENT is below the max volume limit
            if [ $VOLPERCENT -le $MAXVOL ];
            then
                # set volume level in percent
                echo -e setvol +$VOLPERCENT\\nclose | nc -w 1 localhost 6600
            else
                # if we are over the max volume limit, set the volume to maxvol
                echo -e setvol $MAXVOL\\nclose | nc -w 1 localhost 6600
            fi
        else
            # $VOLFILE DOES exist == audio off
            # read volume level from $VOLFILE and set as percent
            echo -e setvol `<$VOLFILE`\\nclose | nc -w 1 localhost 6600
            # delete $VOLFILE
            rm -f $VOLFILE
        fi
        ;;
    volumedown)
        if [ ! -f $VOLFILE ]; then
            if [ -z $VALUE ]; then
		VALUE=1
	    fi
            # $VOLFILE does NOT exist == audio on
			# read volume in percent
			VOLPERCENT=$(echo -e status\\nclose | nc -w 1 localhost 6600 | grep -o -P '(?<=volume: ).*')
			# decrease by $VOLSTEP
                        VOLPERCENT=`expr ${VOLPERCENT} - \( ${VOLSTEP} \* ${VALUE} \)` 
			#decrease volume only if VOLPERCENT is above the min volume limit
			if [ $VOLPERCENT -ge $MINVOL ];
			then
				# set volume level in percent
				echo -e setvol +$VOLPERCENT\\nclose | nc -w 1 localhost 6600
			else
				# if we are below the min volume limit, set the volume to minvol
				echo -e setvol $MINVOL\\nclose | nc -w 1 localhost 6600
			fi
        else
            # $VOLFILE DOES exist == audio off
            # read volume level from $VOLFILE and set as percent
            echo -e setvol `<$VOLFILE`\\nclose | nc -w 1 localhost 6600
            # delete $VOLFILE
            rm -f $VOLFILE
        fi
        ;;
    getvolume)
        # read volume in percent
        VOLPERCENT=$(echo -e status\\nclose | nc -w 1 localhost 6600 | grep -o -P '(?<=volume: ).*')
        echo $VOLPERCENT
	;;
    setmaxvolume)
        # read volume in percent
        VOLPERCENT=$(echo -e status\\nclose | nc -w 1 localhost 6600 | grep -o -P '(?<=volume: ).*')
        # if volume of the box is greater than wanted maxvolume, set volume to maxvolume 
        if [ $VOLPERCENT -gt $VALUE ];
        then
            echo -e setvol $VALUE | nc -w 1 localhost 6600
        fi
        # write new value to file
        echo "$VALUE" > $PATHDATA/../settings/Max_Volume_Limit
        ;;
    getmaxvolume)
        echo $MAXVOL
        ;;
    setvolstep)
        # write new value to file
        echo "$VALUE" > $PATHDATA/../settings/Audio_Volume_Change_Step
        ;;
    getvolstep)
        echo $VOLSTEP
        ;;
    playerstop)
        # stop the player
        $PATHDATA/resume_play.sh -c=savepos && mpc stop
        if [ -e $AUDIOFOLDERSPATH/playing.txt ]
        then
            sudo rm $AUDIOFOLDERSPATH/playing.txt
        fi
        if [ "$DEBUG" == "true" ]; then echo "remove playing.txt" >> $PATHDATA/../logs/debug.log; fi
        ;;
    playerstopafter)
        # stop player after $VALUE minutes
        echo "mpc stop" | at -q s now + $VALUE minute
        ;;
    playernext)
        # play next track in playlist (==folder)
        mpc next
        ;;
    playerprev)
        # play previous track in playlist (==folder)
        mpc prev
        ;;
    playerpause)
        # pause current track
        # mpc knows "pause", which pauses only, and "toggle" which pauses and unpauses, whatever is needed
        mpc toggle
        ;;
    playerplay)
        # play / resume current track
        if [ "$DEBUG" == "true" ]; then echo "Attempting to play: $VALUE" >> $PATHDATA/../logs/debug.log; fi
        # May be called with e.g. -v=1 to start a track in the middle of the playlist.
        # Note: the numbering of the tracks starts with 0, so -v=1 starts the second track
        # of the playlist
        # Another note: "mpc play 1" starts the first track (!)
        # No checking for resume if the audio is paused, just unpause it
        PLAYSTATE=$(echo -e "status\nclose" | nc -w 1 localhost 6600 | grep -o -P '(?<=state: ).*')
        if [ "$PLAYSTATE" == "pause" ]
        then
            echo -e "play $VALUE\nclose" | nc -w 1 localhost 6600
        else
            $PATHDATA/resume_play.sh -c=resume -v=$VALUE
        fi
        ;;
    playerseek)
        # jumps back and forward in track.
        # Usage: ./playout_controls.sh -c=playerseek -v=+15 to jump 15 seconds ahead
        #        ./playout_controls.sh -c=playerseek -v=-10 to jump 10 seconds back
        # Note: Not using "mpc seek" here as it fails if one tries to jump ahead of the beginning of the track
        # (e.g. "mpc seek -15" executed at an elapsed time of 10 seconds let the player hang).
        # mpd seekcur can handle this.
        echo -e "seekcur $VALUE\nclose" | nc -w 1 localhost 6600
        ;;
    playerreplay)
        # start the playing track from beginning
        mpc seek 0
        ;;
    playerrepeat)
        # repeats a single track or a playlist. 
        # Remark: If "single" is "on" but "repeat" is "off", the playout stops after the current song.
        # This command may be called with ./playout_controls.sh -c=playerrepeat -v=single, playlist or off
        case $VALUE in 	
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
        $PATHDATA/resume_play.sh -c=savepos
        mpc clear
	;;
    playlistaddplay)
        # add to playlist (and play)
        # this command clears the playlist, loads a new playlist and plays it. It also handles the resume play feature.
        # FOLDER = rel path from audiofolders
        # VALUE = name of playlist
        if [ "$DEBUG" == "true" ]; then echo "   playlistaddplay VALUE: $VALUE" >> $PATHDATA/../logs/debug.log; fi
        if [ "$DEBUG" == "true" ]; then echo "   playlistaddplay FOLDER: $FOLDER" >> $PATHDATA/../logs/debug.log; fi

        # first clear playlist (and save position if resume play is on)
        $PATHDATA/resume_play.sh -c=savepos
        mpc clear

        # write latest folder played to settings file
        sudo echo ${FOLDER} > $PATHDATA/../settings/Latest_Folder_Played
        sudo chmod 777 $PATHDATA/../settings/Latest_Folder_Played
        if [ "$DEBUG" == "true" ]; then echo "echo ${FOLDER} > $PATHDATA/../settings/Latest_Folder_Played" >> $PATHDATA/../logs/debug.log; fi
        if [ "$DEBUG" == "true" ]; then echo "VAR Latest_Folder_Played: $Latest_Folder_Played" >> $PATHDATA/../logs/debug.log; fi

		# call shuffle_check HERE to enable/disable folder-based shuffeling (mpc shuffle is different to random, because when you shuffle before playing, you start your playlist with a different track EVERYTIME. With random you EVER has the first song and random from track 2.
        mpc load "${VALUE//\//SLASH}" && $PATHDATA/shuffle_play.sh -c=shuffle_check && $PATHDATA/resume_play.sh -c=resume
        if [ "$DEBUG" == "true" ]; then echo "mpc load "${VALUE//\//SLASH}" && $PATHDATA/resume_play.sh -c=resume" >> $PATHDATA/../logs/debug.log; fi
        if [ "$DEBUG" == "true" ]; then echo "entering: shuffle_play.sh to execute shuffle_check" >> $PATHDATA/../logs/debug.log; fi
	;;
    playlistadd)
        # add to playlist, no autoplay
        # save playlist playing
        mpc load "${VALUE}"
        ;;
    setidletime)
        # write new value to file
        echo "$VALUE" > $PATHDATA/../settings/Idle_Time_Before_Shutdown
        # restart service to apply the new value
        sudo systemctl restart phoniebox-idle-watchdog.service &
        ;;
    getidletime)
        echo $IDLETIME
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
	if [[ $(rfkill list wifi | grep -i "Soft blocked: no")  > 0 ]]
	then
	    echo "Wifi will now be deactivated"
	    rfkill block wifi
	else
            echo "Wifi will noow be activated"
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
	    arecord -D plughw:1 --duration=$VALUE -f cd -vv $AUDIOFOLDERSPATH/Recordings/$(date +"%Y-%m-%d_%H-%M-%S").wav &
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
	aplay `ls $AUDIOFOLDERSPATH/Recordings/*.wav -1t|head -1`
	;;
    *)
        echo Unknown COMMAND $COMMAND VALUE $VALUE
        ;;
esac
