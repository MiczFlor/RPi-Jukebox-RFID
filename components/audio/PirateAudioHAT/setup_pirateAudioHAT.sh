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
sudo cp /boot/config.txt /boot/config.txt.bak

echo "gpio=25=op,dh" | sudo tee -a /boot/config.txt > /dev/null
echo "dtoverlay=hifiberry-dac" | sudo tee -a /boot/config.txt > /dev/null

printf "Adding settings to /etc/asound.conf...\n"
# Create backup of /etc/asound.conf if it already exists
if [[ -f /etc/asound.conf ]]; then
    sudo cp /etc/asound.conf /etc/asound.conf.bak
fi

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
if [[ -f /etc/mpd.conf ]]; then
    sudo cp /etc/mpd.conf /etc/mpd.conf.bak
fi

printf "Add hifiberry as audio_output in /etc/mpd.conf...\n"

if ! grep -qe "HiFiBerry DAC+ Lite" /etc/mpd.conf; then
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

printf "You need to reboot to apply the settings.\n"
question "Do you want to reboot now"
sudo reboot
