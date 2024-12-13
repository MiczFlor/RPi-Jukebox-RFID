#!/usr/bin/env bash

# The latest version of SSH installed on the Raspberry Pi 3 uses QoS headers,
# which disagrees with some routers and other hardware. This causes immense
# delays when remotely accessing the RPi over ssh.

source ../includes/02_helpers.sh

if [ -z "$1" ] || { [ "$1" != "enable" ] && [ "$1" != "disable" ]; }; then
    print_lc "Error: Invalid or no argument provided.
Usage: ./ssh_qos.sh <arg>
       where <arg> can be 'enable' or 'disable'"
    exit 1
fi

arg="$1"

if [ "$arg" = "enable" ]; then
    print_lc "Enabling SSH QoS..."
    sudo sed -i '/^IPQoS 0x00 0x00/d' /etc/ssh/sshd_config
    sudo sed -i '/^IPQoS 0x00 0x00/d' /etc/ssh/ssh_config
elif [ "$arg" = "disable" ]; then
    print_lc "Disabling  SSH QoS..."
    echo -e "IPQoS 0x00 0x00\n" | sudo tee -a /etc/ssh/sshd_config
    echo -e "IPQoS 0x00 0x00\n" | sudo tee -a /etc/ssh/ssh_config
fi

# Test
if [ "$arg" = "enable" ]; then
    verify_file_does_not_contain_string "IPQoS 0x00 0x00" "/etc/ssh/sshd_config"
    verify_file_does_not_contain_string "IPQoS 0x00 0x00" "/etc/ssh/ssh_config"
elif [ "$arg" = "disable" ]; then
    verify_file_contains_string_once "IPQoS 0x00 0x00" "/etc/ssh/sshd_config"
    verify_file_contains_string_once "IPQoS 0x00 0x00" "/etc/ssh/ssh_config"
fi
