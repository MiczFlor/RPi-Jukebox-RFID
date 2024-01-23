#!/usr/bin/env bash
source ../includes/02_helpers.sh

if [ -z "$1" ] || { [ "$1" != "enable" ] && [ "$1" != "disable" ]; }; then
    print_lc "Error: Invalid or no argument provided.
Usage: ./ipv6.sh <arg>
       where <arg> can be 'enable' or 'disable'"
    exit 1
fi

arg="$1"

DHCP_CONF_PATH="/etc/dhcpcd.conf"
START_MARKER="## Jukebox IPV6 Config Start"
END_MARKER="## Jukebox IPV6 Config End"

if [ "$arg" = "enable" ]; then
    print_lc "Enabling IPv6..."
    sed -i "/$START_MARKER/,/$END_MARKER/d" "$DHCP_CONF_PATH"
elif [ "$arg" = "disable" ]; then
    print_lc "Disabling IPv6..."
    cp "$DHCP_CONF_PATH" "${DHCP_CONF_PATH}.bak"

    # Only disable if it is enabled
    if ! grep -q "${START_MARKER}" "$DHCP_CONF_PATH"; then
        sudo tee -a $DHCP_CONF_PATH <<-EOF
${START_MARKER}
noarp
ipv4only
noipv6
${END_MARKER}
EOF
    fi
fi

# Test
if [ "$arg" = "enable" ]; then
    verify_file_does_not_contain_string "${START_MARKER}" "${DHCP_CONF_PATH}"
elif [ "$arg" = "disable" ]; then
    verify_file_contains_string_once "${START_MARKER}" "${DHCP_CONF_PATH}"
fi
