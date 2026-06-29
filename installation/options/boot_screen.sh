#!/usr/bin/env bash
source ../includes/02_helpers.sh

if [ -z "$1" ] || { [ "$1" != "enable" ] && [ "$1" != "disable" ]; }; then
    print_lc "Error: Invalid or no argument provided.
Usage: ./boot_screen.sh <arg>
       where <arg> can be 'enable' or 'disable'"
    exit 1
fi

arg="$1"
boot_config_path=$(get_boot_config_path)

_enable_boot_screen() {
    sudo sed -i 's/^disable_splash=1/disable_splash=0/' "$boot_config_path"
    if ! grep -q "^disable_splash" "$boot_config_path"; then
        echo "disable_splash=0" | sudo tee -a "$boot_config_path"
    fi
}

_disable_boot_screen() {
    sudo sed -i 's/^disable_splash=0/disable_splash=1/' "$boot_config_path"
    if ! grep -q "^disable_splash" "$boot_config_path"; then
        echo "disable_splash=1" | sudo tee -a "$boot_config_path"
    fi
}

# Logic
if [ "$arg" = "enable" ]; then
    print_lc "Enabling RPi rainbow screen..."
    _enable_boot_screen
elif [ "$arg" = "disable" ]; then
    print_lc "Disabling RPi rainbow screen..."
    _disable_boot_screen
fi

# Tests
if [ "$arg" = "enable" ]; then
    verify_file_does_not_contain_string "disable_splash=" "${boot_config_path}"
elif [ "$arg" = "disable" ]; then
    verify_file_contains_string_once "disable_splash=1" "${boot_config_path}"
fi
