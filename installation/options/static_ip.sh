#!/usr/bin/env bash

### TODO: Should be converted to NetworkManager

source ../includes/02_helpers.sh

if [ -z "$1" ] || { [ "$1" != "enable" ] && [ "$1" != "disable" ]; }; then
    print_lc "Error: Invalid or no statusument provided.
Usage: ./static_ip.sh <status> <ipaddress>[optional]
       where <status> can be 'enable' or 'disable'"
    exit 1
fi

DHCP_CONF_PATH="/etc/dhcpcd.conf"
START_MARKER="## Jukebox DHCP Config Start"
END_MARKER="## Jukebox DHCP Config End"

CURRENT_ROUTE=$(ip route get 8.8.8.8)
CURRENT_GATEWAY=$(echo "${CURRENT_ROUTE}" | awk '{ print $3; exit }')
CURRENT_INTERFACE=$(echo "${CURRENT_ROUTE}" | awk '{ print $5; exit }')
CURRENT_IP_ADDRESS=$(echo "${CURRENT_ROUTE}" | awk '{ print $7; exit }')

status="$1"
ipaddress="${1:-$CURRENT_IP_ADDRESS}" # No IP address provided, use current IP address

_set_static_ip() {
    local ipaddress="$1"

    # Check static IP has not been set
    if grep -q "${START_MARKER}" "$DHCP_CONF_PATH"; then
        _remove_static_ip
    fi

    log "    ${CURRENT_INTERFACE} is the default network interface"
    log "    ${CURRENT_GATEWAY} is the Router Gateway address"
    log "    Using ${CURRENT_IP_ADDRESS} as the static IP for now"

    sudo tee -a $DHCP_CONF_PATH <<-EOF
${START_MARKER}
interface ${CURRENT_INTERFACE}
static ip_address=${CURRENT_IP_ADDRESS}/24
static routers=${CURRENT_GATEWAY}
static domain_name_servers=${CURRENT_GATEWAY}
${END_MARKER}
EOF
}

_remove_static_ip() {
    sed -i "/$START_MARKER/,/$END_MARKER/d" "$DHCP_CONF_PATH"
}

# Logic
cp "$DHCP_CONF_PATH" "${DHCP_CONF_PATH}.bak"

if [ "$status" = "enable" ]; then
    print_lc "Enabling Static IP..."
    _set_static_ip "$ipaddress"
elif [ "$status" = "disable" ]; then
    print_lc "Disabling Static IP..."
    _remove_static_ip
fi

# Test
if [ "$status" = "enable" ]; then
    verify_file_contains_string_once "${START_MARKER}" "${DHCP_CONF_PATH}"
    verify_file_contains_string "${CURRENT_INTERFACE}" "${DHCP_CONF_PATH}"
    verify_file_contains_string "${ipaddress}" "${DHCP_CONF_PATH}"
    verify_file_contains_string "${CURRENT_GATEWAY}" "${DHCP_CONF_PATH}"
elif [ "$status" = "disable" ]; then
    verify_file_contains_string_once "${START_MARKER}" "${DHCP_CONF_PATH}"
fi
