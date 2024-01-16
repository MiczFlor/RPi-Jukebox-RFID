#!/usr/bin/env bash

# This script follows the official HiFiBerry documentation
# https://www.hifiberry.com/docs/software/configuring-linux-3-18-x/

source ../includes/02_helpers.sh

script_name=$(basename "$0")
boot_config_path=$(get_boot_config_path)

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

example_usage() {
    for key in "${!hifiberry_map[@]}"; do
        description="${hifiberry_map[$key]}"
        echo "$key) $description"
    done
    echo "Example usage: ./${script_name} enable hifiberry-dac"
}

enable_hifiberry() {
    echo "Enabling HiFiBerry board..."
    grep -qxF "^dtoverlay=$1" "$boot_config_path" || echo "dtoverlay=$1" | sudo tee -a "$boot_config_path" > /dev/null
    ./../options/onboard_sound.sh disable
}

disable_hifiberry() {
    echo "Removing existing HiFiBerry configuration..."
    sudo sed -i '/^dtoverlay=hifiberry-/d' "$boot_config_path"
    ./../options/onboard_sound.sh enable
}

check_existing_hifiberry() {
    existing_config=$(grep '^dtoverlay=hifiberry-' "$boot_config_path")
    if [ ! -z "$existing_config" ]; then
        if [ "$1" = "silent" ]; then
            disable_hifiberry
            return 0
        fi

        echo "Existing HiFiBerry configuration detected: $existing_config"
        read -p "Do you want to proceed with a new configuration? This will remove the existing one. (Y/n): " choice
        case $choice in
            [nN][oO]|[nN])
                echo "Exiting without making changes.";
                exit;;
            *)
                disable_hifiberry;
                return 0;;
        esac
    fi
}

# 1-line installation
if [ $# -ge 1 ]; then
    if [[ "$1" != "enable" && "$1" != "disable" ]] || [[ "$1" == "enable" && -z "$2" ]]; then
        echo "Error: Invalid arguments provided.
Usage: ./${script_name} <status> <hifiberry-board>
where <status> can be 'enable' or 'disable'.

The following board options exist:"
        example_usage
        exit 1
    fi

    if [ "$1" == "enable" ]; then
        if [[ -v hifiberry_map["$2"] ]]; then
            check_existing_hifiberry "silent"
            enable_hifiberry "$2"
            exit 1
        fi

        echo "'$2' is not a valid option. You can choose from:"
        example_usage
        exit 1
    fi

    disable_hifiberry
    exit 1
fi

# Guided installation
board_count=${#hifiberry_map[@]}
counter=1

echo "Select your HiFiBerry board:"
for key in "${!hifiberry_map[@]}"; do
    description="${hifiberry_map[$key]}"
    echo "$counter) $description"
    ((counter++))
done
echo "0) Remove existing HiFiBerry configuration"

read -p "Enter your choice (0-$board_count): " choice
case $choice in
    [0])
        disable_hifiberry;
        ;;
    [1-$board_count])
        selected_board=$(get_key_by_item_number hifiberry_map "$choice")
        check_existing_hifiberry
        enable_hifiberry "$selected_board";
        ;;
    *)
        echo "Invalid selection. Exiting.";
        exit 1;;
esac

echo "Configuration complete. Please restart your device."
