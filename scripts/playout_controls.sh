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

####################################
# amixer iface name (e.g. PCM, Speaker, Master)
# 1. create a default if file does not exist
if [ ! -f $PATHDATA/../settings/Audio_iFace_Name ]; then
    echo "PCM" > $PATHDATA/../settings/Audio_iFace_Name
fi
# 2. then|or read value from file
DEVICE=`cat $PATHDATA/../settings/Audio_iFace_Name`

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

#echo $DEVICE
#echo $VOLSTEP
#echo $VOLFILE
#echo `cat $VOLFILE`

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
    sudo pkill vlc
    sleep 1
    /usr/bin/mpg123 $PATHDATA/../misc/shutdownsound.mp3 
    sleep 3
    sudo halt

elif [ "$COMMAND" == "shutdownafter" ]
then
    # remove shutdown times if existent
    for i in `sudo atq -q s | awk '{print $1}'`;do sudo atrm $i;done
    # -c=shutdownafter -v=0 is to remove the shutdown timer
    if [ $VALUE -gt 0 ];
    then
	# shutdown pi after $VALUE minutes
	echo "sudo halt" | at -q s now + $VALUE minute
    fi 

elif [ "$COMMAND" == "reboot" ]
then
    sudo reboot

elif [ "$COMMAND" == "mute" ]
then
    if [ ! -f $VOLFILE ]; then
        # $VOLFILE does NOT exist == audio on
        # read volume in percent and write to $VOLFILE
        amixer sget \'$DEVICE\' | grep -Po -m 1 '(?<=\[)[^]]*(?=%])' > $VOLFILE
        # set volume to 0%
        amixer sset \'$DEVICE\' 0%
    else
        # $VOLFILE DOES exist == audio off
        # read volume level from $VOLFILE and sset as percent
        amixer sset \'$DEVICE\' `<$VOLFILE`%
        # delete $VOLFILE
        rm -f $VOLFILE
    fi
    # alternative pull request: [ ! -e $VOLFILE ] && (amixer sget \'$DEVICE\' | egrep -o '[[:space:]][0-9]+[[:space:]]' | tail -n1> $VOLFILE && amixer sset \'$DEVICE\' 0%) || (amixer sset \'$DEVICE\' `<$VOLFILE` && rm -f $VOLFILE)

elif [ "$COMMAND" == "setvolume" ]
then
    #increase volume only if VOLPERCENT is below the max volume limit
    if [ $VALUE -le $MAXVOL ];
    then
    	# sset volume level in percent
    	amixer sset \'$DEVICE\' $VALUE%
    else
    	# if we are over the max volume limit, set the volume to maxvol
	amixer sset \'$DEVICE\' $MAXVOL%
    fi
    
elif [ "$COMMAND" == "volumeup" ]
then
    if [ ! -f $VOLFILE ]; then
        # $VOLFILE does NOT exist == audio on
        # read volume in percent
        VOLPERCENT=`amixer sget \'$DEVICE\' | grep -Po -m 1 '(?<=\[)[^]]*(?=%])'`
        echo $VOLPERCENT
        # increase by $VOLSTEP
        VOLPERCENT=`expr ${VOLPERCENT} + ${VOLSTEP}` 
        echo $VOLPERCENT
	#increase volume only if VOLPERCENT is below the max volume limit
	if [ $VOLPERCENT -le $MAXVOL ];
	then
        	# sset volume level in percent
        	amixer sset \'$DEVICE\' $VOLPERCENT%
	fi
    else
        # $VOLFILE DOES exist == audio off
        # read volume level from $VOLFILE and sset as percent
        amixer sset \'$DEVICE\' `<$VOLFILE`%
        # delete $VOLFILE
        rm -f $VOLFILE
    fi
    # alternative pull request: [ -e $VOLFILE ] && (vol=`<$VOLFILE` && vol=`expr ${vol} + ${VOLSTEP}` && amixer sset \'$DEVICE\' $vol && rm -f $VOLFILE) || (amixer sset \'$DEVICE\' ${VOLSTEP}+)

elif [ "$COMMAND" == "volumedown" ]
    then
    if [ ! -f $VOLFILE ]; then
        # $VOLFILE does NOT exist == audio on
        # read volume in percent
        VOLPERCENT=`amixer sget \'$DEVICE\' | grep -Po -m 1 '(?<=\[)[^]]*(?=%])'`
        echo $VOLPERCENT
        # decrease by $VOLSTEP
        VOLPERCENT=`expr ${VOLPERCENT} - ${VOLSTEP}` 
        echo $VOLPERCENT
        # sset volume level in percent
        amixer sset \'$DEVICE\' $VOLPERCENT%
    else
        # $VOLFILE DOES exist == audio off
        # read volume level from $VOLFILE and sset as percent
        amixer sset \'$DEVICE\' `<$VOLFILE`%
        # delete $VOLFILE
        rm -f $VOLFILE
    fi
    # alternative pull request: [ -e $VOLFILE ] && (vol=`<$VOLFILE` && vol=`expr ${vol} - ${VOLSTEP}` && amixer sset \'$DEVICE\' $vol && rm -f $VOLFILE) || (amixer sset \'$DEVICE\' ${VOLSTEP}-)

elif [ "$COMMAND" == "getvolume" ]
    then
    # read volume in percent
    VOLPERCENT=`amixer sget \'$DEVICE\' | grep -Po -m 1 '(?<=\[)[^]]*(?=%])'`
    echo $VOLPERCENT

elif [ "$COMMAND" == "setmaxvolume" ]
    then
    # read volume in percent
    VOLPERCENT=`amixer sget \'$DEVICE\' | grep -Po -m 1 '(?<=\[)[^]]*(?=%])'`
    # if volume of the box is greater than wanted maxvolume, set volume to maxvolume 
    if [ $VOLPERCENT -gt $VALUE ];
    then
	amixer sset \'$DEVICE\' $VALUE%
    fi
    # write new value to file
    echo "$VALUE" > $PATHDATA/../settings/Max_Volume_Limit

elif [ "$COMMAND" == "getmaxvolume" ]
    then
    echo $MAXVOL

elif [ "$COMMAND" == "setvolstep" ]
    then
    # write new value to file
    echo "$VALUE" > $PATHDATA/../settings/Audio_Volume_Change_Step

elif [ "$COMMAND" == "getvolstep" ]
    then
    echo $VOLSTEP

elif [ "$COMMAND" == "playerstop" ]
then
    # kill all running VLC media players
    sudo pkill vlc

elif [ "$COMMAND" == "playerstopafter" ]
then
    # stop player after $VALUE minutes
    echo "sudo pkill vlc" | at now + $VALUE minute

# for controlling VLC over rc, see:  
# https://n0tablog.wordpress.com/2009/02/09/controlling-vlc-via-rc-remote-control-interface-using-a-unix-domain-socket-and-no-programming/

elif [ "$COMMAND" == "playernext" ]
then
    # play next track in playlist (==folder)
    echo "next" | nc.openbsd -w 1 localhost 4212

elif [ "$COMMAND" == "playerprev" ]
then
    # play previous track in playlist (==folder)
    echo "prev" | nc.openbsd -w 1 localhost 4212

elif [ "$COMMAND" == "playerpause" ]
then
    # pause current track
    echo "pause" | nc.openbsd -w 1 localhost 4212

elif [ "$COMMAND" == "playerplay" ]
then
    # play / resume current track
    echo "play" | nc.openbsd -w 1 localhost 4212

elif [ "$COMMAND" == "playerreplay" ]
then
    # start the playing track from beginning
    echo "seek 0" | nc.openbsd -w 1 localhost 4212

elif [ "$COMMAND" == "setidletime" ]
then
    # write new value to file
    echo "$VALUE" > $PATHDATA/../settings/Idle_Time_Before_Shutdown
    # restart service to apply the new value
    sudo systemctl restart idle-watchdog.service &

elif [ "$COMMAND" == "getidletime" ]
then
    echo $IDLETIME

else
    echo Unknown COMMAND $COMMAND VALUE $VALUE
fi
