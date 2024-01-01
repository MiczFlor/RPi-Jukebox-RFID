#!/bin/bash

# This script follows the official HiFiBerry documentation
# https://www.hifiberry.com/docs/software/configuring-linux-3-18-x/

source ../includes/02_helpers.sh

# Check if the script is run as root
check_root
boot_config_path=get_boot_config_path

check_existing_hifiberry() {
    existing_config=$(grep 'dtoverlay=hifiberry-' "$boot_config_path")
    if [ ! -z "$existing_config" ]; then
        echo "Existing HiFiBerry configuration detected: $existing_config"
        read -p "Do you want to proceed with a new configuration? This will remove the existing one. (y/n): " yn
        case $yn in
            [Yy]* )
                return 0;;
            [Nn]* )
                echo "Exiting without making changes.";
                exit;;
            * )
                echo "Please answer yes or no.";
                check_existing_hifiberry;;
        esac
    fi
}

remove_existing_hifiberry() {
    echo "Removing existing HiFiBerry configuration..."
    sed -i '/dtoverlay=hifiberry-/d' "$boot_config_path"
    sed -i '/dtoverlay=vc4-fkms-v3d,audio=off/c\dtoverlay=vc4-fkms-v3d' "$boot_config_path"
    sed -i '/dtoverlay=vc4-kms-v3d,noaudio/c\dtoverlay=vc4-kms-v3d' "$boot_config_path"
}

enable_hifiberry() {
    echo "Enabling HiFiBerry board..."
    grep -qxF "dtoverlay=$1" "$boot_config_path" || echo "dtoverlay=$1" >> "$boot_config_path"
}

check_existing_hifiberry

# List of HiFiBerry boards
echo "
Select your HiFiBerry board:
1) DAC (HiFiBerry MiniAmp, I2S PCM5102A DAC)
2) HiFiBerry DAC+ Standard/Pro/Amp2
3) HiFiBerry DAC2 HD
4) HiFiBerry DAC+ ADC
5) HiFiBerry DAC+ ADC Pro
6) HiFiBerry Digi+
7) HiFiBerry Digi+ Pro
8) HiFiBerry Amp+ (not Amp2)
9) HiFiBerry Amp3"
read -p "Enter your choice (1-10): " choice

# Enable selected HiFiBerry board
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

remove_existing_hifiberry

echo "Disabling onboard sound..."
sed -i '/dtparam=audio=on/c\dtparam=audio=off' "$boot_config_path"

if grep -qx 'dtoverlay=vc4-fkms-v3d' "$boot_config_path"; then
    echo "Disabling audio in vc4-fkms-v3d overlay..."
    sed -i '/dtoverlay=vc4-fkms-v3d/c\dtoverlay=vc4-fkms-v3d,audio=off' "$boot_config_path"
fi

if grep -qx 'dtoverlay=vc4-kms-v3d' "$boot_config_path"; then
    echo "Disabling audio in vc4-kms-v3d overlay..."
    sed -i '/dtoverlay=vc4-kms-v3d/c\dtoverlay=vc4-kms-v3d,noaudio' "$boot_config_path"
fi

if [ -z "${CONFIGURE_ALSA}" ]; then
    echo "CONFIGURE_ALSA not set. Skipping configuration of sound settings in asound.conf."
else
    if [ "${CONFIGURE_ALSA}" == "true" ]; then
        if [ -f /etc/asound.conf ]; then
            echo "Backing up existing asound.conf..."
            cp /etc/asound.conf "/etc/asound.conf.backup.$(date +%Y%m%d%H%M%S)"
        fi

        card_id=$(cat /proc/asound/cards | grep -oP '(?<=^ )\d+(?= \[sndrpihifiberry\]:)' | head -n 1)

        if [ -z "$card_id" ]; then
            echo "  Error: Could not find HifiBerry sound card in /etc/asound.conf."
        else
            echo "Configuring sound settings in asound.conf..."
    cat > /etc/asound.conf << EOF
pcm.hifiberry {
    type softvol
    slave.pcm "plughw:$card_id"
    control.name "HifiBerry"
    control.card $card_id
}

pcm.!default {
    type plug
    slave.pcm "hifiberry"
}
EOF
        fi
    fi
fi

echo "Configuration complete. Please restart your device."
