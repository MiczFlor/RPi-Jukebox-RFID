#!/bin/bash

# Check that script is called from source directory
FILE=bt-sink-switch.py
if [ ! -f "$FILE" ]; then
  echo -e "Error: Install script must be started from source directoy of bt-headphones!"
  exit -1
fi

# Only works for the Classic edition
EDITIONFILE=../../settings/edition
if [ ! -f "$EDITIONFILE" ]; then
  echo -e "Error: Cannot find file '$EDITIONFILE' to check Phonibox edition"
  exit -1

fi

EDITION=`cat $EDITIONFILE`
if [ "${EDITION}" != "classic" ]; then
  echo -e "Error: Sorry, this feature is only working with the classic edition, but got '${EDITION}'"
  exit -1
fi

USER=`whoami`
SCRPATH=`pwd`

# Ensure script is executable for everyone
sudo chmod ugo+rx $FILE

# Make sure required packages are installed
echo -e "\nChecking bluetooth packages"
sudo apt install bluetooth -y

# Add users to bluetooth, to make bluetooth control available through web interface
echo -e "\nSetting up user rights"
sudo usermod -G bluetooth -a www-data
sudo usermod -G bluetooth -a ${USER}

# Add www-data to allow gpio control (for LED support)
sudo usermod -G gpio -a www-data

# Let global controls know this feature is enabled
echo -e "\nLet global controls know this feature is enabled"
CONFFILE=../../settings/bluetooth-sink-switch
echo "enabled" > ${CONFFILE}
chmod ugo+rw ${CONFFILE}

# Restart web service to take notice of new user rights
sudo systemctl restart lighttpd.service

# Final notes
echo -e "\n\n\nIMPORTANT NOTE:\nPlease modify ${FILE} around line 20 for\n  led_pin=None\nto configure LED pin-out.\n Do nothing to leave it disabled."
