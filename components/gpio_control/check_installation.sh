#!/bin/bash

FRED="\033[31m"
FBOLD='\033[1;31m'
RS="\033[0m"

ERROR=false
for SERVICE_NAME in "phoniebox-gpio-buttons.service" "phoniebox-rotary-encoder.service"
do
    echo "checking ${SERVICE_NAME}"
    if [ "$(systemctl is-active ${SERVICE_NAME})" = "active" ]; then 
        echo -e "$FRED"$FBOLD" ${SERVICE_NAME} is still active $RS"
        ERROR=true
    fi
done




SERVICE_STATUS="$(systemctl is-active phoniebox_gpio_control.service)"
if [ "${SERVICE_STATUS}" = "active" ]; then
    echo "Phoniebox GPIO Service started correctly ....."
else
    ERROR=true
    echo ""
    echo -e "$FRED"$FBOLD"Problem during installation occured $RS"
    echo "   Service not running, please check functionallity by running gpio_control.py "
    echo "   in the directory ~/RPi-Jukebox-RFID/components/gpio_control: "
    echo "      $ cd ~/RPi-Jukebox-RFID/components/gpio_control"
    echo "      $ python gpio_control.py"
    echo "   or check output of journaclctl by:"
    echo "      $ journalctl -u phoniebox_gpio_control.service -f"
fi
echo
if $ERROR ; then
    echo -e "$FRED"$FBOLD"PROBLEM IN INSTALLATION $RS"
else
    echo 'Installation seems to be fine'
fi
