#!/bin/bash

# Check that script is called from source directory
FILE=bt-buttons.py
if [ ! -f "$FILE" ]; then
  echo -e "Error: Install script must be started from source directoy of bt-headphones!"
  exit -1
fi

USER=`whoami`
SCRPATH=`pwd`

# Configuring service file
echo -e "\nConfiguring service"
sed "s@WorkingDirectory.*@WorkingDirectory=${SCRPATH}@g" phoniebox-bt-buttons.service.sample > phoniebox-bt-buttons.service.configured
sed -i "s@ExecStart.*@ExecStart=${SCRPATH}/${FILE} > /dev/null@g" phoniebox-bt-buttons.service.configured

# Install service and enable it
SSRC=phoniebox-bt-buttons.service.configured
SDST=/etc/systemd/system/phoniebox-bt-buttons.service
echo -e "\nInstalling service"
sudo mv -f ${SSRC} ${SDST}
sudo chown root:root ${SDST}
sudo chmod 644 ${SDST}
sudo systemctl enable phoniebox-bt-buttons.service
sudo systemctl start phoniebox-bt-buttons.service

# Final notes
echo -e "\n\nIMPORTANT NOTE:\nThis feature requires a certain amount of customization to each headset. Check out $FILE for details."
echo -e "If experimenting with the script make sure the service is stopped:\n  sudo systemctl stop phoniebox-bt-buttons.service\n\n"
