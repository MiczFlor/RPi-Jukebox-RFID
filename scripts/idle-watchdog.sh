#!/bin/bash
#Remove old shutdown commands from all 'at' queues after boot to prevent immediate shutdown
for i in `sudo atq | awk '{print $1}'`;do sudo atrm $i;done
#Give the RPi enough time to get the correct time via network, no need for any hurry
sleep 60

PATHDATA="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Idle time after the RPi will be shut down. 0=turn off feature.
# 1. create a default if file does not exist
if [ ! -f $PATHDATA/../settings/Idle_Time_Before_Shutdown ]; then
    echo "0" > $PATHDATA/../settings/Idle_Time_Before_Shutdown
fi
# 2. then|or read value from file
IDLETIME=`cat $PATHDATA/../settings/Idle_Time_Before_Shutdown`

# amixer iface name (e.g. PCM, Speaker, Master)
# 1. create a default if file does not exist
if [ ! -f $PATHDATA/../settings/Audio_iFace_Name ]; then
    echo "PCM" > $PATHDATA/../settings/Audio_iFace_Name
fi
# 2. then|or read value from file
DEVICE=`cat $PATHDATA/../settings/Audio_iFace_Name`

#Go into infinite loop if idle time is greater 0
while [ $IDLETIME -gt 0 ]
do
	#Read volume and vlc status
	VOLPERCENT=`amixer sget \'$DEVICE\' | grep -Po -m 1 '(?<=\[)[^]]*(?=%])'`
	VLCSTATUS=`echo "status" | nc.openbsd -w 1 localhost 4212`
	sleep 3

	#Set shutdown time if no idle shutdown time is set when vlc is not playing or volume is 0
	if { [ "$(echo "$VLCSTATUS" | grep -c "state playing")" == "0" ] || [ $VOLPERCENT -eq "0" ]; } && [ -z "$(sudo atq -q i)" ]; 
	then
		# shutdown pi after idling for $IDLETIME minutes
		for i in `sudo atq -q i | awk '{print $1}'`;do sudo atrm $i;done
		sleep 1		
		echo "sudo halt" | at -q i now + $IDLETIME minute
	fi
	
	# If vlc is playing and volume is greater 0, remove idle shutdown. Skip this if 'at'-queue is already empty
	if [ "$(echo "$VLCSTATUS" | grep -c "state playing")" == "1" ] && [ $VOLPERCENT -ne "0" ] && [ -n "$(sudo atq -q i)" ];
	then
		for i in `sudo atq -q i | awk '{print $1}'`;do sudo atrm $i;done
	fi	
	
	sleep 60
done
