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

if [ "$arg" = "enable" ]; then
    print_lc "Enabling RPi rainbow screen..."
    sudo raspi-config nonint do_boot_splash 0
elif [ "$arg" = "disable" ]; then
    print_lc "Disabling RPi rainbow screen..."
    sudo raspi-config nonint do_boot_splash 1
fi

# Test, no test required. Depending on raspi-config to test
