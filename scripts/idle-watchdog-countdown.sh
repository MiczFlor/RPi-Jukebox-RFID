#!/bin/bash

# This is a mpd idle watchdog to shutdown the box.
# 
# Phonieboxes without reliable system time can use this idle-watchdog-script to
# shutdown the box after a pre defined number of minutes.
# This script checks every 60 seconds if mpd is paying music with volume set to
# greater than 0. If not it decreases the pre-defined number of minutes and shut
# down the box if it reaches zero.
# Be aware that playing lots of short sequences (less than 60 seconds) could be 
# undetected by this script and lead to an unwanted shutdown.

# Check for idle time settings. Assume to disable automatic shudown if not set.
if [ ! -r ./settings/Idle_Time_Before_Shutdown ]; then
    logger "Idle_Time_Before_Shutdown is not set. Disable idle watchdog!"
    exit 0
else
    SHUTDOWNAFTER=$(cat ./settings/Idle_Time_Before_Shutdown | head -n 1)
fi

# Check if setting is a numeric value; else warn and disable watchdog.
[ "$SHUTDOWNAFTER" -eq "$SHUTDOWNAFTER" ] 2>/dev/null
if [ $? -ne 0 ]; then
    logger "Invalid settings for Idle_Time_Before_Shutdown (not numeric). Disable idle watchdog!"
    exit 0
fi

COUNTDOWN=$SHUTDOWNAFTER # initialize countdown value

# start the continuous loop
while [ $SHUTDOWNAFTER -gt 0 ]; do
    # check if mpd is playing and volume is not 0
    if [ $(mpc | egrep -c '^\[playing\]') -eq 1 ] && [ $(mpc | egrep -c '^volume:\s+0%') -eq 0 ]; then
        if [ $COUNTDOWN -ne $SHUTDOWNAFTER ]; then
            logger "mpd is playing audible again. Stop countdown to shutdown."
        fi
        COUNTDOWN=$SHUTDOWNAFTER # re-init countdown
    else
        if [ $COUNTDOWN -gt 0 ]; then
            logger "mpd is NOT playing audible. Shutdown in $COUNTDOWN minutes."
        else
            logger "mpd was NOT playing audible for $SHUTDOWNAFTER minutes. Shutdown system!"
            ./scripts/playout_controls.sh -c=shutdownsilent
	    exit 0
        fi
        COUNTDOWN=$(expr $COUNTDOWN - 1)
    fi
    sleep 60
done

exit 0
