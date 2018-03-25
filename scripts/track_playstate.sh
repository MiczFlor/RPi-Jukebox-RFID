#!/bin/bash

# Polls vlc for track played and time lapsed.
# Removes played items from the playlist

# Definitions
PATHDATA="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
CURRENTTRACKFILE=$PATHDATA/../playlists/$1.track
CURRENTPLAYLIST=$PATHDATA/../playlists/$1.m3u


# While VLC is running. If VLC ends (either by stop or end of playlist) tracking will also stop

while pgrep vlc >/dev/null; do


	# Get last entry in the currenttrack from file to remove it from the playlist if its done playing
	PREVIOUSTRACK=`sed -n 1p $CURRENTTRACKFILE | cut -c 9-`
	
	# send status request to host, find the file name in the output and cut the last blank from the output.
	# If you find a better regex to not have that trailing space, go for it.
	CURRENTTRACK=`echo status | nc.openbsd -w 1 localhost 4212 | grep -Po 'new input: file://\K[^)]+' | rev | cut -c 2- | rev`

	# Same for time: send time request to host and cut it so only the actual time is left
	CURRENTTIME=`echo get_time | nc.openbsd -w 1 localhost 4212 | sed -n 3p | cut -c 3-`
	
	# Check if PREVIOUSTRACK is empty (first time playlist is running) and fill it with current if so
	if [ ! $PREVIOUSTRACK]
	then
		PREVIOUSTRACK=$CURRENTTRACK
	fi

	# Write track and time info to the playlist folder into a file named after the folder
	echo 'Track :' $CURRENTTRACK > $CURRENTTRACKFILE
	echo 'Time :' $CURRENTTIME >> $CURRENTTRACKFILE
		
	# If the track changed (previous is not the same as current), delete the previous entry from the playlist
	
	if [ "$CURRENTTRACK" != "$PREVIOUSTRACK" ]
	then
		TODELETE=`grep -n "$PREVIOUSTRACK" $CURRENTPLAYLIST | cut -c 1`d
		`sudo sed -i $TODELETE $CURRENTPLAYLIST`
	fi
		
	# Do this every 5 seconds. Can be tuned but will lower accuracy
	sleep 5s
	
done

