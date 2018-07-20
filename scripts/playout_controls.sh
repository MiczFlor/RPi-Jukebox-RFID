#!/bin/bash

# This shell script contains all the functionality to control
# playout and change volume and the like.
# This script is called from the web app and the bash script.
# The purpose is to have all playout logic in one place, this
# makes further development and potential replacement of 
# the playout player easier.

# $DEBUG true|false
# prints $COMMAND in the terminal
DEBUG=false

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

#echo $VOLSTEP
#echo $VOLFILE
#echo $MAXVOL
#echo `cat $VOLFILE`
#echo $IDLETIME

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

if [ "$COMMAND" == "shutdown" ]
then
    if [ "$DEBUG" == "true" ]; then echo "$COMMAND"; fi
    $PATHDATA/resume_play.sh -c=savepos && mpc clear
    sleep 1
    /usr/bin/mpg123 $PATHDATA/../misc/shutdownsound.mp3 
    sleep 3
    sudo halt

elif [ "$COMMAND" == "shutdownsilent" ]
then
    # doesn't play a shutdown sound
    if [ "$DEBUG" == "true" ]; then echo "$COMMAND"; fi
    $PATHDATA/resume_play.sh -c=savepos && mpc clear
    sudo halt

elif [ "$COMMAND" == "shutdownafter" ]
then
    # remove shutdown times if existent
    if [ "$DEBUG" == "true" ]; then echo "$COMMAND"; fi
    for i in `sudo atq -q t | awk '{print $1}'`;do sudo atrm $i;done
    # -c=shutdownafter -v=0 is to remove the shutdown timer
    if [ $VALUE -gt 0 ];
    then
        # shutdown pi after $VALUE minutes
        echo "$PATHDATA/playout_controls.sh -c=shutdownsilent" | at -q t now + $VALUE minute
    fi 

elif [ "$COMMAND" == "reboot" ]
then
    if [ "$DEBUG" == "true" ]; then echo "$COMMAND"; fi
    $PATHDATA/resume_play.sh -c=savepos && mpc clear
    sudo reboot

elif [ "$COMMAND" == "mute" ]
then
    if [ "$DEBUG" == "true" ]; then echo "$COMMAND"; fi
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

elif [ "$COMMAND" == "setvolume" ]
then
    if [ "$DEBUG" == "true" ]; then echo "$COMMAND"; fi
    #increase volume only if VOLPERCENT is below the max volume limit
    if [ $VALUE -le $MAXVOL ];
    then
        # set volume level in percent
        echo -e setvol $VALUE\\nclose | nc -w 1 localhost 6600
    else
        # if we are over the max volume limit, set the volume to maxvol
        echo -e setvol $MAXVOL\\nclose | nc -w 1 localhost 6600
    fi
    
elif [ "$COMMAND" == "volumeup" ]
then
    if [ "$DEBUG" == "true" ]; then echo "$COMMAND"; fi
    if [ ! -f $VOLFILE ]; then
        # $VOLFILE does NOT exist == audio on
        # read volume in percent
        VOLPERCENT=$(echo -e status\\nclose | nc -w 1 localhost 6600 | grep -o -P '(?<=volume: ).*')
        # increase by $VOLSTEP
        #increase volume only if VOLPERCENT is below the max volume limit
        if [ $VOLPERCENT -le $MAXVOL ];
        then
            # set volume level in percent
            echo -e volume +$VOLSTEP\\nclose | nc -w 1 localhost 6600
        fi
    else
        # $VOLFILE DOES exist == audio off
        # read volume level from $VOLFILE and set as percent
        echo -e setvol `<$VOLFILE`\\nclose | nc -w 1 localhost 6600
        # delete $VOLFILE
        rm -f $VOLFILE
    fi

elif [ "$COMMAND" == "volumedown" ]
then
    if [ "$DEBUG" == "true" ]; then echo "$COMMAND"; fi
    if [ ! -f $VOLFILE ]; then
        # $VOLFILE does NOT exist == audio on
        # read volume in percent
        VOLPERCENT=$(echo -e status\\nclose | nc -w 1 localhost 6600 | grep -o -P '(?<=volume: ).*')
        # decrease by $VOLSTEP
        # set volume level in percent
        echo -e volume -$VOLSTEP\\nclose | nc -w 1 localhost 6600
    else
        # $VOLFILE DOES exist == audio off
        # read volume level from $VOLFILE and set as percent
        echo -e setvol `<$VOLFILE`\\nclose | nc -w 1 localhost 6600
        # delete $VOLFILE
        rm -f $VOLFILE
    fi

elif [ "$COMMAND" == "getvolume" ]
then
    # read volume in percent
    if [ "$DEBUG" == "true" ]; then echo "$COMMAND"; fi
    VOLPERCENT=$(echo -e status\\nclose | nc -w 1 localhost 6600 | grep -o -P '(?<=volume: ).*')
    echo $VOLPERCENT

elif [ "$COMMAND" == "setmaxvolume" ]
then
    # read volume in percent
    if [ "$DEBUG" == "true" ]; then echo "$COMMAND"; fi
    VOLPERCENT=$(echo -e status\\nclose | nc -w 1 localhost 6600 | grep -o -P '(?<=volume: ).*')
    # if volume of the box is greater than wanted maxvolume, set volume to maxvolume 
    if [ $VOLPERCENT -gt $VALUE ];
    then
        echo -e setvol $VALUE | nc -w 1 localhost 6600
    fi
    # write new value to file
    echo "$VALUE" > $PATHDATA/../settings/Max_Volume_Limit

elif [ "$COMMAND" == "getmaxvolume" ]
then
    if [ "$DEBUG" == "true" ]; then echo "$COMMAND"; fi
    echo $MAXVOL

elif [ "$COMMAND" == "setvolstep" ]
then
    # write new value to file
    if [ "$DEBUG" == "true" ]; then echo "$COMMAND"; fi
    echo "$VALUE" > $PATHDATA/../settings/Audio_Volume_Change_Step

elif [ "$COMMAND" == "getvolstep" ]
then
    if [ "$DEBUG" == "true" ]; then echo "$COMMAND"; fi
    echo $VOLSTEP

elif [ "$COMMAND" == "playerstop" ]
then
    # stop the player
    if [ "$DEBUG" == "true" ]; then echo "$COMMAND"; fi
    $PATHDATA/resume_play.sh -c=savepos && mpc stop

elif [ "$COMMAND" == "playerstopafter" ]
then
    # stop player after $VALUE minutes
    if [ "$DEBUG" == "true" ]; then echo "$COMMAND"; fi
    echo "mpc stop" | at -q s now + $VALUE minute

elif [ "$COMMAND" == "playernext" ]
then
    # play next track in playlist (==folder)
    if [ "$DEBUG" == "true" ]; then echo "$COMMAND"; fi
    mpc next

elif [ "$COMMAND" == "playerprev" ]
then
    # play previous track in playlist (==folder)
    if [ "$DEBUG" == "true" ]; then echo "$COMMAND"; fi
    mpc prev

elif [ "$COMMAND" == "playerpause" ]
then
    # pause current track
    # mpc knows "pause", which pauses only, and "toggle" which pauses and unpauses, whatever is needed
    if [ "$DEBUG" == "true" ]; then echo "$COMMAND"; fi
    mpc toggle
    
elif [ "$COMMAND" == "playerplay" ]
then
    # play / resume current track
    # No checking for resume if the audio is paused, just unpause it
    if [ "$DEBUG" == "true" ]; then echo "$COMMAND"; fi
    PLAYSTATE=$(echo -e status\\nclose | nc -w 1 localhost 6600 | grep -o -P '(?<=state: ).*')
    if [ "$PLAYSTATE" == "pause" ]
    then
        mpc play
    else
        $PATHDATA/resume_play.sh -c=resume
    fi
    
elif [ "$COMMAND" == "playerreplay" ]
then
    # start the playing track from beginning
    if [ "$DEBUG" == "true" ]; then echo "$COMMAND"; fi
    mpc seek 0

elif [ "$COMMAND" == "playlistclear" ]
then
    # clear playlist
    if [ "$DEBUG" == "true" ]; then echo "$COMMAND"; fi
    $PATHDATA/resume_play.sh -c=savepos
    mpc clear

elif [ "$COMMAND" == "playlistaddplay" ]
then
    # add to playlist (and play)
    if [ "$DEBUG" == "true" ]; then echo "$COMMAND"; fi
    mpc load "${VALUE}" && $PATHDATA/resume_play.sh -c=resume
    if [ "$DEBUG" == "true" ]; then echo "mpc load "${VALUE}" && $PATHDATA/resume_play.sh -c=resume"; fi

elif [ "$COMMAND" == "playlistadd" ]
then
    # add to playlist, no autoplay
    if [ "$DEBUG" == "true" ]; then echo "$COMMAND"; fi
    mpc load "${VALUE}"

elif [ "$COMMAND" == "setidletime" ]
then
    # write new value to file
    if [ "$DEBUG" == "true" ]; then echo "$COMMAND"; fi
    echo "$VALUE" > $PATHDATA/../settings/Idle_Time_Before_Shutdown
    # restart service to apply the new value
    sudo systemctl restart idle-watchdog.service &

elif [ "$COMMAND" == "getidletime" ]
then
    if [ "$DEBUG" == "true" ]; then echo "$COMMAND"; fi
    echo $IDLETIME

else
    echo Unknown COMMAND $COMMAND VALUE $VALUE
fi
