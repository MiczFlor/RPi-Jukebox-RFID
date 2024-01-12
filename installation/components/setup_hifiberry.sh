#!/usr/bin/env bash

# This script follows the official HiFiBerry documentation
# https://www.hifiberry.com/docs/software/configuring-linux-3-18-x/

source ../includes/02_helpers.sh

script_name=$(basename "$0")

declare -A hifiberry_map=(
    ["hifiberry-dac"]="DAC (HiFiBerry MiniAmp, I2S PCM5102A DAC)"
    ["hifiberry-dacplus"]="HiFiBerry DAC+ Standard/Pro/Amp2"
    ["hifiberry-dacplushd"]="HiFiBerry DAC2 HD"
    ["hifiberry-dacplusadc"]="HiFiBerry DAC+ ADC"
    ["hifiberry-dacplusadcpro"]="HiFiBerry DAC+ ADC Pro"
    ["hifiberry-digi"]="HiFiBerry Digi+"
    ["hifiberry-digi-pro"]="HiFiBerry Digi+ Pro"
    ["hifiberry-amp"]="HiFiBerry Amp+ (not Amp2)"
    ["hifiberry-amp3"]="HiFiBerry Amp3"
)

# 1-line installation
if [ $# -ge 1 ];
    if { ([ "$1" != "enable" ] && [ "$1" != "disable" ]) || ([ "$1" -= "enable" ] && [ $# -ge 2 ]); }
        echo "Error: Invalid provided.
Usage: ./${script_name} <status> <hifiberry-board>[optional]
where <status> can be 'enable' or 'disable'"
        exit 1
    fi

    if [ "$1" != "enable" ];
        case "$2" in
        "${hifiberry_list[@]}")
            echo "Variable is in the list."
            ;;
        *)
            echo "'$2' is not a valid option. You can choose from:"
            for key in "${!hifiberry_descriptions[@]}"; do
                description="${hifiberry_descriptions[$key]}"
                echo "$key) $description"
            done
            echo "Example usage: ./${script_name} enable hifiberry-dac"
            ;;
        esac


    fi
fi

# Guided installation
boot_config_path=$(get_boot_config_path)
asound_conf_path="/etc/asound.conf"

disable_hifiberry() {
    echo "Removing existing HiFiBerry configuration..."
    sudo sed -i '/dtoverlay=hifiberry-/d' "$boot_config_path"
    sudo sed -i '/dtoverlay=vc4-fkms-v3d,audio=off/c\dtoverlay=vc4-fkms-v3d' "$boot_config_path"
    sudo sed -i '/dtoverlay=vc4-kms-v3d,noaudio/c\dtoverlay=vc4-kms-v3d' "$boot_config_path"
    mv -f "$asound_conf_path" "/etc/asound.conf.bak" 2>/dev/null
}

check_existing_hifiberry() {
    existing_config=$(grep 'dtoverlay=hifiberry-' "$boot_config_path")
    if [ ! -z "$existing_config" ]; then
        echo "Existing HiFiBerry configuration detected: $existing_config"
        read -p "Do you want to proceed with a new configuration? This will remove the existing one. (Y/n): " yn
        case $yn in
            [nN][oO]|[nN])
                echo "Exiting without making changes.";
                exit;;
            *)
                disable_hifiberry;
                return 0;;
        esac
    fi
}

enable_hifiberry() {
    echo "Enabling HiFiBerry board..."
    grep -qxF "dtoverlay=$1" "$boot_config_path" || echo "dtoverlay=$1" >> "$boot_config_path"
}

check_existing_hifiberry

# List of HiFiBerry boards
echo "Select your HiFiBerry board:"
for key in "${!hifiberry_descriptions[@]}"; do
    description="${hifiberry_descriptions[$key]}"
    echo "$key) $description"
done

read -p "Enter your choice (0-9): " choice

case $choice in
    [0])
        disable_hifiberry;
        exit 1;;
    [1-9])
        selected_board="${hifiberry_descriptions[$choice]}";
        enable_hifiberry "$selected_board";
        return 0;;
    *)
        echo "Invalid selection. Exiting.";
        exit 1;;
esac

echo "Disabling onboard sound..."
sudo sed -i "s/^\(dtparam=\([^,]*,\)*\)audio=\(on\|true\|yes\|1\)\(.*\)/\1audio=off\4/g" "$boot_config_path"

if grep -qx 'dtoverlay=vc4-fkms-v3d' "$boot_config_path"; then
    echo "Disabling audio in vc4-fkms-v3d overlay..."
    sudo sed -i '/dtoverlay=vc4-fkms-v3d/c\dtoverlay=vc4-fkms-v3d,audio=off' "$boot_config_path"
fi

if grep -qx 'dtoverlay=vc4-kms-v3d' "$boot_config_path"; then
    echo "Disabling audio in vc4-kms-v3d overlay..."
    sudo sed -i '/dtoverlay=vc4-kms-v3d/c\dtoverlay=vc4-kms-v3d,noaudio' "$boot_config_path"
fi

if [ -z "${CONFIGURE_ALSA}" ]; then
    echo "CONFIGURE_ALSA not set. Skipping configuration of sound settings in asound.conf."
else
    if [ "${CONFIGURE_ALSA}" == "true" ]; then
        if [ -f "$asound_conf_path" ]; then
            echo "Backing up existing asound.conf..."
            cp -f "$asound_conf_path" "/etc/asound.conf.bak"
        fi

        card_id=$(cat /proc/asound/cards | grep -oP '(?<=^ )\d+(?= \[sndrpihifiberry\]:)' | head -n 1)

        if [ -z "$card_id" ]; then
            echo "Error: Could not find HifiBerry sound card in $asound_conf_path."
        else
            echo "Configuring sound settings in $asound_conf_path..."
            cat > "$asound_conf_path" << EOF
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
