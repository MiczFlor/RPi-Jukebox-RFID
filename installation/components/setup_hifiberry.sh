#!/bin/bash

# Check if the script is run as root
if [ "$(id -u)" != "0" ]; then
   echo "This script must be run as root" 1>&2
   exit 1
fi

# Disable onboard sound of Raspberry Pi
echo "Disabling onboard sound..."
sed -i '/dtparam=audio=on/c\dtparam=audio=off' /boot/config.txt

# Enable HiFiBerry board
echo "Enabling HiFiBerry board..."
grep -qxF 'dtoverlay=hifiberry-dac' /boot/config.txt || echo 'dtoverlay=hifiberry-dac' >> /boot/config.txt

# Backup asound.conf
if [ -f /etc/asound.conf ]; then
    echo "Backing up existing asound.conf..."
    cp /etc/asound.conf "/etc/asound.conf.backup.$(date +%Y%m%d%H%M%S)"
fi

echo "Configuring sound settings..."
cat > /etc/asound.conf << EOF
pcm.hifiberry {
    type softvol
    slave.pcm "plughw:0"
    control.name "HifiBerry"
    control.card 0
}

pcm.!default {
    type plug
    slave.pcm "hifiberry"
}
EOF

echo "Configuration complete. Please restart your device."
