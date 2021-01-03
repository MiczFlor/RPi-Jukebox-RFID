#!/usr/bin/env bash

HOME_DIR="/home/pi"
JUKEBOX_HOME_DIR="${HOME_DIR}/RPi-Jukebox-RFID"

TYPE=$1

if [[ -n "$TYPE" ]]; then
    echo "Configuring Hifiberry ${TYPE} sound card"
else
    echo "Error: please pass miniamp or amp2 to script."
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

printf "Please make sure that the Hifiberry is connected...\n"
question "Continue"

printf "Adding settings to /boot/config.txt...\n"
if [[ ! -f /boot/config.txt.bak ]]; then
    sudo cp /boot/config.txt /boot/config.txt.bak
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
mixer_control_name="Master" # for miniamp

if [ "${TYPE}" == "amp2" ]; then
    # see https://github.com/MiczFlor/RPi-Jukebox-RFID/issues/1198#issuecomment-750757106
    mixer_control_name="Digital"
fi

sudo sed -i -E "s/^(\s*mixer_control\s*\")[^\"]*(\"\s*# optional)/\1\\${mixer_control_name}\2/" /etc/mpd.conf

printf "You should reboot later to apply the settings.\n"
