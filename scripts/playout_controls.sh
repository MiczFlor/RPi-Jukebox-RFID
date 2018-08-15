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

# SET VARIABLES
# The variables can be changed in the ../settings dir.
# Relevant files are:
# * ../settings/Audio_Volume_Change_Step
# * ../settings/Audio_iFace_Name

# The absolute path to the folder whjch contains all the scripts.
# Unless you are working with symlinks, leave the following line untouched.
PATHDATA="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
if [ $DEBUG == "true" ]; then echo "## SCRIPT playout_controls.sh ($NOW) ##" >> $PATHDATA/../logs/debug.log; fi

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
for i in "$@"
do
    case $i in
        -c=*|--command=*)
        COMMAND="${i#*=}"
        ;;
        -v=*|--value=*)
        VALUE="${i#*=}"
        ;;
    esac
done
if [ $DEBUG == "true" ]; then echo "VAR COMMAND: $COMMAND" >> $PATHDATA/../logs/debug.log; fi
if [ $DEBUG == "true" ]; then echo "VAR VALUE: $VALUE" >> $PATHDATA/../logs/debug.log; fi
        
case $COMMAND in 
    shutdown)
        $PATHDATA/resume_play.sh -c=savepos && mpc clear
    	#remove shuffle mode
	if [ -e $AUDIOFOLDERSPATH/random.txt ]
        then
            sudo rm $AUDIOFOLDERSPATH/random.txt
            mpc random off
        fi
	sleep 1
        /usr/bin/mpg123 $PATHDATA/../shared/shutdownsound.mp3 
        sleep 3
        sudo halt
        ;;
    shutdownsilent)
        # doesn't play a shutdown sound
        $PATHDATA/resume_play.sh -c=savepos && mpc clear
        #remove shuffle mode
        if [ -e $AUDIOFOLDERSPATH/random.txt ]
        then
            sudo rm $AUDIOFOLDERSPATH/random.txt
            mpc random off
        fi
	sudo halt
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
	#remove shuffle mode
        if [ -e $AUDIOFOLDERSPATH/random.txt ]
        then
            sudo rm $AUDIOFOLDERSPATH/random.txt
            mpc random off
        fi
        sudo reboot
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
            # $VOLFILE does NOT exist == audio on
            # read volume in percent
            VOLPERCENT=$(echo -e status\\nclose | nc -w 1 localhost 6600 | grep -o -P '(?<=volume: ).*')
            # increase by $VOLSTEP
	    VOLPERCENT=`expr ${VOLPERCENT} + ${VOLSTEP}` 
            #increase volume only if VOLPERCENT is below the max volume limit
            if [ $VOLPERCENT -le $MAXVOL ];
            then
                # set volume level in percent
                echo -e volume +$VOLSTEP\\nclose | nc -w 1 localhost 6600
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
            # $VOLFILE does NOT exist == audio on
            # decrease by $VOLSTEP
            echo -e volume -$VOLSTEP\\nclose | nc -w 1 localhost 6600
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
        if [ $DEBUG == "true" ]; then echo "Attempting to play: $VALUE" >> $PATHDATA/../logs/debug.log; fi
        # May be called with e.g. -v=1 to start a track in the middle of the playlist.
        # Note: the numbering of the tracks starts with 0, so -v=1 starts the second track
        # of the playlist
        # Another note: "mpc play 1" starts the first track (!)
        # No checking for resume if the audio is paused, just unpause it
        PLAYSTATE=$(echo -e "status\nclose" | nc -w 1 localhost 6600 | grep -o -P '(?<=state: ).*')
        if [ "$PLAYSTATE" == "pause" ]
        then
            echo -e "play $VALUE" | nc -w 1 localhost 6600
        else
            $PATHDATA/resume_play.sh -c=resume -v=$VALUE
        fi
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
        # activates random file order permanently (not only the current playlist)
        # Remark: IF $AUDIOFOLDERSPATH/random.txt exists, random will be deactivated 
        # This command may be called with ./playout_controls.sh -c=playershuffle
	if [ -e $AUDIOFOLDERSPATH/random.txt ]
        then
            sudo rm $AUDIOFOLDERSPATH/random.txt
	    mpc random off
        else
	    sudo echo $VALUE > $AUDIOFOLDERSPATH/random.txt
	    mpc random on
	fi
	;;
    playlistclear)
        # clear playlist
        $PATHDATA/resume_play.sh -c=savepos
        mpc clear
	;;
    playlistaddplay)
        # add to playlist (and play)
        if [ $DEBUG == "true" ]; then echo "   playlistaddplay VALUE: $VALUE" >> $PATHDATA/../logs/debug.log; fi
        
        # save playlist playing
        sudo echo $VALUE > $AUDIOFOLDERSPATH/playing.txt 
        
        # write latest folder played to settings file
        # Chances are, this was already written in 'rfid_trigger_play.sh'
        # However, new development might jump right here and not pipe
        # through 'rfid_trigger_play.sh'
        #echo $VALUE > $PATHDATA/../settings/Latest_Folder_Played
        # clear track(s) from playlist
        mpc clear
        mpc load "${VALUE}" && $PATHDATA/resume_play.sh -c=resume
        if [ "$DEBUG" == "true" ]; then echo "mpc load "${VALUE}" && $PATHDATA/resume_play.sh -c=resume"; fi
        ;;
    playlistadd)
        # add to playlist, no autoplay
        # save playlist playing
        sudo echo $VALUE > $AUDIOFOLDERSPATH/playing.txt 
        mpc load "${VALUE}"
        ;;
    setidletime)
        # write new value to file
        echo "$VALUE" > $PATHDATA/../settings/Idle_Time_Before_Shutdown
        # restart service to apply the new value
        sudo systemctl restart idle-watchdog.service &
        ;;
    getidletime)
        echo $IDLETIME
        ;;
    *)
        echo Unknown COMMAND $COMMAND VALUE $VALUE
        ;;
esac
