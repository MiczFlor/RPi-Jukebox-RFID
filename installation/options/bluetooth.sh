#!/usr/bin/env bash
source ../includes/02_helpers.sh

if [ -z "$1" ] || { [ "$1" != "enable" ] && [ "$1" != "disable" ]; }; then
    print_lc "Error: Invalid or no argument provided.
Usage: ./bluetooth.sh <arg>
       where <arg> can be 'enable' or 'disable'"
    exit 1
fi

arg="$1"

if [ "$arg" = "enable" ]; then
    print_lc "Enabling Bluetooth..."
    sudo systemctl enable hciuart.service
    sudo systemctl enable bluetooth.service
elif [ "$arg" = "disable" ]; then
    print_lc "Disabling Bluetooth..."
    sudo systemctl disable hciuart.service
    sudo systemctl disable bluetooth.service
fi

# Test
if [ "$arg" = "enable" ]; then
    verify_optional_service_enablement hciuart.service enabled
    verify_optional_service_enablement bluetooth.service enabled
elif [ "$arg" = "disable" ]; then
    verify_optional_service_enablement hciuart.service disabled
    verify_optional_service_enablement bluetooth.service disabled
fi
