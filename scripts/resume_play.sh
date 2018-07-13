#!/bin/bash

# This script saves or restores the last position (song and time) in a playlist (=folder)
# Saving and restoring will only be made if a "lastplayed.dat" file is found in the folder where the 
# audio is stored.
# Usage: 
# Save the position: ./resume_play.sh -c=savepos
# Restore position and play: ./resume_play-sh -c=resume
# Enable resume for folder: ./resume_play-sh -c=enableresume -v=foldername_in_audiofolders
# Disable resume for folder: ./resume_play-sh -c=disableresume -v=foldername_in_audiofolders
#
# Call this script with "savepos" everytime
# - before you clear the playlist (mpc clear)
# - before you stop the player
# - before you shutdown the Pi (maybe not necessary as mpc stores the position between reboots, but it feels saver)


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



PATHDATA="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Get folder name of currently played audio by extracting the playlist name 
FOLDER=$(mpc lsplaylists)

case "$COMMAND" in

savepos)
	# Check if "lastplayed.dat" exists
	if [ -e "$PATHDATA/../shared/audiofolders/$FOLDER/lastplayed.dat" ];
	then
		# Get the elapsed time of the currently played audio file from mpd
		ELAPSED=$(echo -e "status\nclose" | nc.openbsd -w 1 localhost 6600 | grep -o -P '(?<=elapsed: ).*')
		# mpd reports an elapsed time only if the audio is playing or is paused. Check if we got an elapsed time
		if [ ! -z $ELAPSED ]; # Why does -n not work here?
		then
			#Get the filename of the currently played audio
			CURRENTFILENAME=$(echo -e "currentsong\nclose" | nc -w 1 localhost 6600 | grep -o -P '(?<=file: ).*')
			# Save filename and time to lastplayed.dat
			printf "$CURRENTFILENAME\n$ELAPSED" > "$PATHDATA/../shared/audiofolders/$FOLDER/lastplayed.dat"
			echo $FOLDER
		fi
	fi
;;
resume)
	# Check if "lastplayed.dat" exists
	if [ -e "$PATHDATA/../shared/audiofolders/$FOLDER/lastplayed.dat" ];
	then
		# Read the last played filename and timestamp from lastplayed.dat
		FILENAME=$(head -n 1 "$PATHDATA/../shared/audiofolders/$FOLDER/lastplayed.dat")
		TIMESTAMP=$(tail -n 1 "$PATHDATA/../shared/audiofolders/$FOLDER/lastplayed.dat")

		# Get the playlist position of the file from mpd
		# Alternative approach: "mpc searchplay xx && mpc seek yy" 
		PLAYLISTPOS=$(echo -e playlistfind filename \"$FILENAME\"\\nclose | nc.openbsd -w 1 localhost 6600 | grep -o -P '(?<=Pos: ).*')

		# If the file is found, it is played from timestamp, otherwise start playlist from beginning
		if [ ! -z $PLAYLISTPOS ];
		then
			echo -e seek $PLAYLISTPOS $TIMESTAMP \\nclose | nc.openbsd -w 1 localhost 6600
		else
			mpc play
		fi
	else
		# if no lastplayed.dat exists, we play the playlist from the beginning
		mpc play
	fi
;;
enableresume)
	echo -e "filename\n0" > "$PATHDATA/../shared/audiofolders/$VALUE/lastplayed.dat"
;;
disableresume)
	rm "$PATHDATA/../shared/audiofolders/$VALUE/lastplayed.dat"
;;
*)
	echo "Command unknown"
;;
esac
