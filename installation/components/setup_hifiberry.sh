#!/bin/bash

# This script follows the official HiFiBerry documentation
# https://www.hifiberry.com/docs/software/configuring-linux-3-18-x/

# Check if the script is run as root
if [ "$(id -u)" != "0" ]; then
   echo "This script must be run as root" 1>&2
   exit 1
fi

# List of HiFiBerry boards
echo -m "\n
Select your HiFiBerry board:
1) DAC for Raspberry Pi 1/DAC+ Light/DAC Zero/MiniAmp/Beocreate/DAC+ DSP/DAC+ RTC
2) DAC+ Standard/Pro/Amp2
3) DAC2 HD
4) DAC+ ADC
5) DAC+ ADC Pro
6) Digi+
7) Digi+ Pro
8) Amp+ (not Amp2)
9) Amp3"
read -p "Enter your choice (1-9): " choice

enable_hifiberry() {
    echo "Enabling HiFiBerry board..."
    grep -qxF "dtoverlay=$1" /boot/config.txt || echo "dtoverlay=$1" >> /boot/config.txt
}

case $choice in
    1) enable_hifiberry "hifiberry-dac";;
    2) enable_hifiberry "hifiberry-dacplus";;
    3) enable_hifiberry "hifiberry-dacplushd";;
    4) enable_hifiberry "hifiberry-dacplusadc";;
    5) enable_hifiberry "hifiberry-dacplusadcpro";;
    6) enable_hifiberry "hifiberry-digi";;
    7) enable_hifiberry "hifiberry-digi-pro";;
    8) enable_hifiberry "hifiberry-amp";;
    9) enable_hifiberry "hifiberry-amp3";;
    *) echo "Invalid selection. Exiting."; exit 1;;
esac

echo "Disabling onboard sound..."
sed -i '/dtparam=audio=on/c\dtparam=audio=off' /boot/config.txt

if grep -q 'dtoverlay=vc4-fkms-v3d' /boot/config.txt; then
    echo "Disabling audio in vc4-fkms-v3d overlay..."
    sed -i '/dtoverlay=vc4-fkms-v3d/c\dtoverlay=vc4-fkms-v3d,audio=off' /boot/config.txt
fi

if grep -q 'dtoverlay=vc4-kms-v3d' /boot/config.txt; then
    echo "Disabling audio in vc4-kms-v3d overlay..."
    sed -i '/dtoverlay=vc4-kms-v3d/c\dtoverlay=vc4-kms-v3d,noaudio' /boot/config.txt
fi

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
