#!/usr/bin/env bash

if [[ $(id -u) != 0 ]]; then
   echo "This script should be run using sudo"
   exit 1
fi

if [[ ! -f ~/.config/phoniebox/gpio_settings.ini ]]; then
    mkdir -p ~/.config/phoniebox && cp /example_configs/gpio_settings.ini ~/.config/phoniebox/gpio_settings.ini
fi

echo 'disable old services: phoniebox-gpio-buttons and phoniebox-rotary-encoder'
systemctl stop phoniebox-rotary-encoder.service
systemctl disable phoniebox-rotary-encoder.service
systemctl stop phoniebox-gpio-buttons.service
systemctl disable phoniebox-gpio-buttons.service

echo 'Install all required python modules'
python3 -m pip install --upgrade --force-reinstall -r requirements.txt

echo
echo 'Installing GPIO_Control service'
read -p "Press enter to continue " -n 1 -r
SERVICE_FILE=/etc/systemd/system/phoniebox-gpio-control.service
if [[ -f "$SERVICE_FILE" ]]; then
   echo "$SERVICE_FILE exists.";
   echo 'systemctl daemon-reload'
   systemctl daemon-reload
   echo 'restarting service'
   systemctl restart phoniebox-gpio-control.service
   read -p "Press enter to continue " -n 1 -r;

    #echo "systemctl daemon-reload"
    #systemctl daemon-reload
else
    cp -v ../../misc/sampleconfigs/phoniebox-gpio-control.service.sample /etc/systemd/system/phoniebox-gpio-control.service
    echo "systemctl start phoniebox-gpio-control.service"
    echo 'systemctl daemon-reload'
    systemctl start phoniebox-gpio-control.service
    echo "systemctl enable phoniebox-gpio-control.service"
    systemctl enable phoniebox-gpio-control.service
fi
SERVICE_STATUS="$(systemctl is-active phoniebox-gpio-control.service)"
if [[ "${SERVICE_STATUS}" = "active" ]]; then
    echo "Phoniebox GPIO Service started correctly ....."
    echo "For further configuration of GPIO-devices consult the wiki:
https://github.com/chbuehlmann/RPi-Jukebox-RFID/wiki/Using-GPIO-hardware-buttons"
else
    echo ""
    FRED="\033[31m"
    FBOLD='\033[1;31m'
    RS="\033[0m"
    echo -e "$FRED"$FBOLD"Problem during installation occured $RS"
    echo "   Service not running, please check functionallity by running gpio_control.py "
    echo "   in the directory ~/RPi-Jukebox-RFID/components/gpio_control: "
    echo "      $ cd ~/RPi-Jukebox-RFID/components/gpio_control"
    echo "      $ python gpio_control.py"
    echo "   or check output of journaclctl by:"
    echo "      $ journalctl -u phoniebox-gpio-control.service -f"
    exit 1
fi
#systemctl is-active --quiet phoniebox_gpio_control.service
#systemctl status phoniebox_gpio_control.service

