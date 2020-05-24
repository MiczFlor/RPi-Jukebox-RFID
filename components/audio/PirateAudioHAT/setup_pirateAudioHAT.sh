#!/usr/bin/env bash

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

printf "Stopping and disabling GPIO button service...\n"
#TODO this might not be necessary
sudo systemctl stop phoniebox-gpio-buttons.service
sudo systemctl disable phoniebox-gpio-buttons.service

printf "Adding settings to /boot/config.txt...\n"
if [[ ! -f /boot/config.txt.bak ]]; then
    sudo cp /boot/config.txt /boot/config.txt.bak
fi

# Only add the two lines, if they do not exist already
if ! sudo grep -qe "gpio=25=op,dh" /boot/config.txt; then
    echo "gpio=25=op,dh" | sudo tee -a /boot/config.txt > /dev/null
fi
if ! sudo grep -qe "dtoverlay=hifiberry-dac" /boot/config.txt; then
    echo "dtoverlay=hifiberry-dac" | sudo tee -a /boot/config.txt > /dev/null
fi

printf "Adding settings to /etc/asound.conf...\n"
# Create backup of /etc/asound.conf if it already exists
if [[ -f /etc/asound.conf && ! -f /etc/asound.conf.bak ]]; then
    sudo cp /etc/asound.conf /etc/asound.conf.bak
fi

# Do not add, but replace content if file already exists
sudo tee /etc/asound.conf << EOF > /dev/null
pcm.hifiberry {
    type            softvol
    slave.pcm       "plughw:CARD=sndrpihifiberry,DEV=0"
    control.name    "Master"
    control.card    1
}
pcm.!default {
    type            plug
    slave.pcm       "hifiberry"
}
ctl.!default {
    type            hw
    card            1
}
EOF

# Create backup of /etc/mpd.conf if it already exists
if [[ -f /etc/mpd.conf && ! -f /etc/mpd.conf.bak ]]; then
    sudo cp /etc/mpd.conf /etc/mpd.conf.bak
fi

printf "Add hifiberry as audio_output in /etc/mpd.conf...\n"
# Only add, if it does not exist already
if ! sudo grep -qe "HiFiBerry DAC+ Lite" /etc/mpd.conf; then
    sudo sed -i "/# An example of an ALSA output:/ r /dev/stdin" /etc/mpd.conf <<'EOG'
audio_output {
        enabled         "yes"
        type            "alsa"
        name            "HiFiBerry DAC+ Lite"
        device          "hifiberry"
        auto_resample   "no"
        auto_channels   "no"
        auto_format     "no"
        dop             "no"
}
EOG
else
    printf "/etc/mpd.conf is already configured. Skipping...\n"
fi

printf "Set mixer_control name in /etc/mpd.conf...\n"
mixer_control_name="Master"
sudo sed -i -E "s/^(\s*mixer_control\s*\")[^\"]*(\"\s*# optional)/\1\\${mixer_control_name}\2/" /etc/mpd.conf

printf "Activating SPI...\n"
sudo raspi-config nonint do_spi 0

printf "Installing Python dependencies...\n"
sudo apt-get -y -qq install python3-pil python3-numpy

printf "Installing mopidy plugins...\n"
sudo pip3 --quiet install Mopidy-PiDi pidi-display-pil pidi-display-st7789 mopidy-raspberry-gpio

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

printf "You need to reboot to apply the settings.\n"
question "Do you want to reboot now"
sudo reboot
