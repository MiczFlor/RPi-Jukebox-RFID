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
if [ $# -ge 1 ]; then
    if { ([ "$1" != "enable" ] && [ "$1" != "disable" ]) || ([ "$1" -= "enable" ] && [ $# -ge 2 ]); }; then
        echo "Error: Invalid provided.
Usage: ./${script_name} <status> <hifiberry-board>[optional]
where <status> can be 'enable' or 'disable'"
        exit 1
    fi

    if [ "$1" != "enable" ]; then
        case "$2" in
        "${hifiberry_map[@]}")
            return 0;;
        *)
            echo "'$2' is not a valid option. You can choose from:"
            for key in "${!hifiberry_map[@]}"; do
                description="${hifiberry_map[$key]}"
                echo "$key) $description"
            done
            echo "Example usage: ./${script_name} enable hifiberry-dac"
            exit 1
            ;;
        esac
    fi
fi

# Guided installation
boot_config_path=$(get_boot_config_path)

enable_hifiberry() {
    echo "Enabling HiFiBerry board..."
    grep -qxF "dtoverlay=$1" "$boot_config_path" || sudo echo "dtoverlay=$1" >> "$boot_config_path"
}

disable_hifiberry() {
    echo "Removing existing HiFiBerry configuration..."
    ./../options/onboard_sound.sh enable
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

prompt_board_list() {
    board_count=${#hifiberry_map[@]}

    counter=1
    echo "Select your HiFiBerry board:"
    for key in "${!hifiberry_map[@]}"; do
        description="${hifiberry_map[$key]}"
        echo "$counter) $description"
        ((counter++))
    done

    read -p "Enter your choice (1-$board_count): " choice

    case $choice in
        [0])
            disable_hifiberry;
            exit 1;;
        [1-$board_count])
            selected_board=$(get_key_by_item_number hifiberry_map "$choice")
            enable_hifiberry "$selected_board";
            return 0;;
        *)
            echo "Invalid selection. Exiting.";
            exit 1;;
    esac
}

# Execute program
check_existing_hifiberry
prompt_board_list
./../options/onboard_sound.sh disable

echo "Configuration complete. Please restart your device."
