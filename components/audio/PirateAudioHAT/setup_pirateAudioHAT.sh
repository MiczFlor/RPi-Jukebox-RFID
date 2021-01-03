#!/usr/bin/env bash

HOME_DIR="/home/pi"
JUKEBOX_HOME_DIR="${HOME_DIR}/RPi-Jukebox-RFID"

EDITION=$1

if [[ -n "$EDITION" ]]; then
    echo "Configuring Pirate Audio HAT for ${EDITION} edition"
else
    echo "Error: please pass classic or spotify to script."
    exit -1
fi

question() {
    local question=$1
    read -p "${question} (y/n)? " choice
    case "$choice" in
      y|Y ) ;;
      n|N ) exit 0;;
      * ) echo "Error: invalid" ; question ${question};;
    esac
}

printf "Please make sure that the Pirate Audio HAT is connected...\n"
question "Continue"

if [ "${EDITION}" == "spotify" ]; then
    printf "Stopping and disabling GPIO control service...\n"
    sudo systemctl stop phoniebox-gpio-control.service
    sudo systemctl disable phoniebox-gpio-control.service
fi

printf "Adding settings to /boot/config.txt...\n"
if [[ ! -f /boot/config.txt.bak ]]; then
    sudo cp /boot/config.txt /boot/config.txt.bak
fi

# Only add the two lines, if they do not exist already
if ! sudo grep -qe "gpio=25=op,dh" /boot/config.txt; then
    echo "gpio=25=op,dh" | sudo tee -a /boot/config.txt > /dev/null
fi

bash "${JUKEBOX_HOME_DIR}/component/audio/Hifiberry/setup_Hifiberry.sh"

printf "Activating SPI...\n"
sudo raspi-config nonint do_spi 0

printf "Installing Python dependencies...\n"
sudo apt-get -y -qq install python3-pil python3-numpy

if [ "${EDITION}" == "spotify" ]; then
    printf "Installing Python packages...\n"
    sudo python3 -m pip install --upgrade --force-reinstall -q -r "${JUKEBOX_HOME_DIR}"/components/audio/PirateAudioHAT/requirements-mopidy.txt

    # Only add, if it does not exist already
    printf "Editing mopidy configuration...\n"
    if ! sudo grep -qe "raspberry-gpio" /etc/mopidy/mopidy.conf; then
        sudo tee -a /etc/mopidy/mopidy.conf << EOH > /dev/null

[raspberry-gpio]
enabled = true
bcm5 = play_pause,active_low,150
bcm6 = volume_down,active_low,150
bcm16 = next,active_low,150
bcm20 = volume_up,active_low,150

[pidi]
enabled = true
display = st7789
EOH
    else
        printf "/etc/mopidy/mopidy.conf is already configured. Skipping...\n"
    fi

    printf "Enable access for modipy user...\n"
    sudo usermod -a -G spi,i2c,gpio,video mopidy
else
    printf "Installing Python packages...\n"
    sudo python3 -m pip install --upgrade --force-reinstall -q -r "${JUKEBOX_HOME_DIR}"/components/audio/PirateAudioHAT/requirements.txt

    cp "${JUKEBOX_HOME_DIR}"/misc/sampleconfigs/gpio_settings.ini.pirate-audio-hat.sample "${JUKEBOX_HOME_DIR}"/settings/gpio_settings.ini

    sudo cp "${JUKEBOX_HOME_DIR}"/misc/sampleconfigs/phoniebox-pirateaudio-display.service.sample "/etc/systemd/system/phoniebox-pirateaudio-display.service"
    sudo chown root:root /etc/systemd/system/phoniebox-pirateaudio-display.service
    sudo chmod 644 /etc/systemd/system/phoniebox-pirateaudio-display.service
    # enable the services needed
    sudo systemctl enable phoniebox-pirateaudio-display

    # restart services
    sudo systemctl restart phoniebox-gpio-control
    sudo systemctl restart phoniebox-pirateaudio-display
fi

printf "You need to reboot to apply the settings.\n"
question "Do you want to reboot now"
sudo reboot
