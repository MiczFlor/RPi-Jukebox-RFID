#!/usr/bin/env bash
source ../includes/02_helpers.sh

if [ -z "$1" ] || { [ "$1" != "enable" ] && [ "$1" != "disable" ]; }; then
    print_lc "Error: Invalid or no argument provided.
Usage: ./systemctl_services.sh <arg>
       where <arg> can be 'enable' or 'disable'"
    exit 1
fi

arg="$1"

if [ "$arg" = "enable" ]; then
    print_lc "Enable default services..."

    sudo systemctl enable keyboard-setup.service
    sudo systemctl enable triggerhappy.service
    sudo systemctl enable triggerhappy.socket
    sudo systemctl enable raspi-config.service
    sudo systemctl enable apt-daily.service
    sudo systemctl enable apt-daily-upgrade.service
    sudo systemctl enable apt-daily.timer
    sudo systemctl enable apt-daily-upgrade.timer
elif [ "$arg" = "disable" ]; then
    print_lc "Disable default services..."

    sudo systemctl disable keyboard-setup.service
    sudo systemctl disable triggerhappy.service
    sudo systemctl disable triggerhappy.socket
    sudo systemctl disable raspi-config.service
    sudo systemctl disable apt-daily.service
    sudo systemctl disable apt-daily-upgrade.service
    sudo systemctl disable apt-daily.timer
    sudo systemctl disable apt-daily-upgrade.timer
fi

# Test
if [ "$arg" = "enable" ]; then
    verify_optional_service_enablement keyboard-setup.service enabled
    verify_optional_service_enablement triggerhappy.service enabled
    verify_optional_service_enablement triggerhappy.socket enabled
    verify_optional_service_enablement raspi-config.service enabled
    verify_optional_service_enablement apt-daily.service enabled
    verify_optional_service_enablement apt-daily-upgrade.service enabled
    verify_optional_service_enablement apt-daily.timer enabled
    verify_optional_service_enablement apt-daily-upgrade.timer enabled

elif [ "$arg" = "disable" ]; then
    verify_optional_service_enablement keyboard-setup.service disabled
    verify_optional_service_enablement triggerhappy.service disabled
    verify_optional_service_enablement triggerhappy.socket disabled
    verify_optional_service_enablement raspi-config.service disabled
    verify_optional_service_enablement apt-daily.service disabled
    verify_optional_service_enablement apt-daily-upgrade.service disabled
    verify_optional_service_enablement apt-daily.timer disabled
    verify_optional_service_enablement apt-daily-upgrade.timer disabled
fi
