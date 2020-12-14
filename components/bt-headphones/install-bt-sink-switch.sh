#!/bin/bash

# Check that script is called from source directory
FILE=bt-sink-switch.py
if [ ! -f "$FILE" ]; then
  echo -e "Error: Install script must be started from source directoy og bt-headphones!"
  exit -1
fi

USER=`whoami`
SCRPATH=`pwd`

# Ensure script is executable for everyone
sudo chmod ugo+x $FILE

# Make sure required packages are installed
echo -e "\nChecking bluetooth packages"
#sudo apt install bluetooth -y

# Add users to bluetooth, to make bluetooth control avaiable through web interface
echo -e "\nSetting up user rights"
#sudo usermod -G bluetooth -a www-data
#sudo usermod -G bluetooth -a ${USER}

# Default to speaker sink after boot
#STARTUP=../../scripts/startup-scripts.sh
STARTEXISTS=0
if [ -f ${STARTUP} ]; then
    # Check if script is already registed with startup-scripts.sh
    STARTEXISTS=`grep -c ${FILE} ${STARTUP}`
fi
if [ "${STARTEXISTS}" = 0 ]; then 
    echo -e "\nRegistering start-up script"
    echo -e "\n#Default audio sink to speakers irrespective of setting at shutdown" >> $STARTUP
    echo -e "${SCRPATH}/bt-sink-switch.py speakers\n" >> $STARTUP
fi

# Register script is enabled at global controls
# TBD

# Final notes
echo -e "\n\n\nIMPORTANT NOTE:\nPlease modify ${FILE} around line 20 for\n  led_pin=6\nto configure LED pin-out or diable LED support altogether." 

