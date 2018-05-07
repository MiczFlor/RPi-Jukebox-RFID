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
# reboot
# setvolume
# volumeup
# volumedown
# playerstop
# playerquit
# playernext
# playerprev
# playerpause 
# playerreplay
# restartlist

# SET VARIABLES
# Here you can tweak the commands a little

# amixer default sound device (e.g. PCM, MASTER)
DEVICE=PCM

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

if [ $COMMAND == "shutdown" ]
then
    sudo halt

elif [ $COMMAND == "reboot" ]
then
    sudo reboot

elif [ $COMMAND == "mute" ]
then
    echo '{"command": ["cycle", "mute"]} ' | socat - /tmp/mpvsocket

elif [ $COMMAND == "setvolume" ]
then
    echo "set volume $VALUE" | socat - /tmp/mpvsocket

elif [ $COMMAND == "volumeup" ]
then
    echo "add volume +10" | socat - /tmp/mpvsocket

elif [ $COMMAND == "volumedown" ]
then
    echo "add volume -10" | socat - /tmp/mpvsocket

elif [ $COMMAND == "playerstop" ]
then
    echo quit-watch-later | socat - /tmp/mpvsocket

elif [ $COMMAND == "playerquit" ]
then
    echo quit | socat - /tmp/mpvsocket

elif [ $COMMAND == "playernext" ]
then
    echo playlist_next | socat - /tmp/mpvsocket

elif [ $COMMAND == "playerprev" ]
then
    echo playlist_prev | socat - /tmp/mpvsocket

elif [ $COMMAND == "playerpause" ]
then
    echo '{ "command": ["cycle", "pause"] }' | socat - /tmp/mpvsocket

elif [ $COMMAND == "playerreplay" ]
then
    # start the playing track from beginning
    echo "seek 0 absolute-percent" | socat - /tmp/mpvsocket
elif [ $COMMAND == "restartlist" ]
then
    echo "set playlist-pos 0" | socat - /tmp/mpvsocket

else
    echo Unknown COMMAND $COMMAND VALUE $VALUE
fi
