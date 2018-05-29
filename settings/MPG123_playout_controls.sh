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

case $COMMAND in 
	init)
    		#nohup bash -c "exec -a RPi-Jukebox-Player mpg123 -R --fifo /tmp/mpg123.socket" &>/dev/null &    
	        nohup bash -c "exec -a RPi-Jukebox-Player tmux new-session -s Jukebox-Player '/home/pi/RPi/mpg123-1.23.8/scripts/conplay" >> /tmp/RPi-Jukebox_Player.nohup 2>&1 &  
    		sleep 0.2
    		echo "SILENCE" > /tmp/mpg123.socket
		;;
	shutdown)
    		sudo halt
		;;
	reboot)
		sudo reboot
		;;

	play)
	        nohup bash -c "exec -a RPi-Jukebox-Player tmux new-session -d -s Jukebox-Player '/home/pi/RPi-Jukebox-RFID/scripts/conplay $VALUE'" >> /tmp/RPi-Jukebox_Player.nohup 2>&1 &  
		;;
	mute)
		amixer sset \'$DEVICE\' 0%
		;;

	setvolume)
		amixer sset \'$DEVICE\' $VALUE%
		;;
	volumeup)
		amixer sset \'$DEVICE\' 500+
		;;
	volumedown)
		amixer sset \'$DEVICE\' 500-
		;;
	playerstop)
		tmux send-keys -t Jukebox-Player 's' C-m
		;;
	playerquit)
		tmux send-keys -t Jukebox-Player 'q' C-m
		;;
	playernext)
		tmux send-keys -t Jukebox-Player 'f' C-m
		;;
	playerprev)
		tmux send-keys -t Jukebox-Player 'd' C-m
		;;
	playerpause)
		tmux send-keys -t Jukebox-Player 's' C-m
		;;
	playerreplay)
		# start the playing track from beginning
		tmux send-keys -t Jukebox-Player 'b' C-m
		;;
	restartlist)
		sed -e 's/#.*$//' -e '/^$/d' $VALUE
	        nohup bash -c "exec -a RPi-Jukebox-Player tmux new-session -s Jukebox-Player '/home/pi/RPi-Jukebox-RFID/scripts/conplay $VALUE'" >> /tmp/RPi-Jukebox_Player.nohup 2>&1 &  
		;;
	*)
		echo Unknown COMMAND $COMMAND VALUE $VALUE
		;;
esac
