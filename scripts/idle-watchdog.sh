#!/bin/bash
#Remove old shutdown commands from all 'at' queues after boot to prevent immediate shutdown
for i in `sudo atq | awk '{print $1}'`;do sudo atrm $i;done
#Give the RPi enough time to get the correct time via network
#Otherwise there may be an immediate shutdown because this script may set a shutdown time dated in the past
#in the first loop. If the Pi gets a correct time via network, "at" suddenly detects a overdue job, which is:
#shutting down the Pi.  
sleep 60

PATHDATA="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Idle time after the RPi will be shut down. 0=turn off feature.
# 1. create a default if file does not exist
if [ ! -f $PATHDATA/../settings/Idle_Time_Before_Shutdown ]; then
    echo "0" > $PATHDATA/../settings/Idle_Time_Before_Shutdown
fi
# 2. then|or read value from file
IDLETIME=`cat $PATHDATA/../settings/Idle_Time_Before_Shutdown`

#Go into infinite loop if idle time is greater 0
while [ $IDLETIME -gt 0 ]
do
    #Read volume and player status
    PLAYERSTATUS=$(mpc status)
    VOLPERCENT=$(echo -e "status\nclose" | nc.openbsd -w 1 localhost 6600 | grep -o -P '(?<=volume: ).*')
    sleep 1
    #Set shutdown time if box is not playing or volume is 0 and no idle shutdown time is set
    if { [ "$(echo "$PLAYERSTATUS" | grep -c "\[playing\]")" == "0" ] || [ $VOLPERCENT -eq "0" ]; } && [ -z "$(sudo atq -q i)" ]; 
    then
        # shutdown pi after idling for $IDLETIME minutes
        for i in `sudo atq -q i | awk '{print $1}'`;do sudo atrm $i;done
        sleep 1
        echo "$PATHDATA/playout_controls.sh -c=shutdownsilent" | at -q i now + $IDLETIME minute
    fi

    # If box is playing and volume is greater 0, remove idle shutdown. Skip this if "at"-queue is already empty
    if [ "$(echo "$PLAYERSTATUS" | grep -c "\[playing\]")" == "1" ] && [ $VOLPERCENT -ne "0" ] && [ -n "$(sudo atq -q i)" ];
    then
        for i in `sudo atq -q i | awk '{print $1}'`;do sudo atrm $i;done
    fi

    sleep 60
done
