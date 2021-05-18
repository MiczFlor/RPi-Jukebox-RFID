#!/bin/bash

FILE=bt-buttons.py
REGFILE=bt-buttons-register-device.py

# Check that script is called from source directory
if [ ! -f "$FILE" ]; then
  echo -e "Error: Install script must be started from source directoy of bt-headphones!"
  exit -1
fi

USER=`whoami`
SCRPATH=`pwd`

chmod ugo+rx ${FILE}
chmod ugo+rx ${REGFILE}

# Configuring service file
echo -e "\nConfiguring service"
SERVICESAMPLE=../../../misc/sampleconfigs/phoniebox-bt-buttons.service.sample
sed "s@WorkingDirectory.*@WorkingDirectory=${SCRPATH}@g" ${SERVICESAMPLE} > phoniebox-bt-buttons.service.configured
sed -i "s@ExecStart.*@ExecStart=${SCRPATH}/${FILE}@g" phoniebox-bt-buttons.service.configured

# Install service and enable it
SSRC=phoniebox-bt-buttons.service.configured
SDST=/etc/systemd/system/phoniebox-bt-buttons.service
echo -e "\nInstalling service"
sudo mv -f ${SSRC} ${SDST}
sudo chown root:root ${SDST}
sudo chmod 644 ${SDST}
sudo systemctl enable phoniebox-bt-buttons.service


# Call the register-device script
# Do this last, so that user can re-run abortive device registration without having to run the installer again
echo -e "\n\n*******************************************************************"
echo -e "Will try to register bluetooth input device. If this fails, you can re-start the device registration by calling \n $ ./${REGFILE}"
echo -e "Don't forget to reboot or restart the phoniebox-bt-buttons.service afterwards!"
echo -e "*******************************************************************\n\n"
./${REGFILE}

# Start the service for immediate use
sudo systemctl start phoniebox-bt-buttons.service

# Final notes
echo -e "\n\nIMPORTANT NOTE:\nThis feature MAY require a certain amount of customization to some headsets. Check out the README.md for details."
echo -e "\n\nEverything is set up now and should work now. In case of doubt, reboot!\n\n"
