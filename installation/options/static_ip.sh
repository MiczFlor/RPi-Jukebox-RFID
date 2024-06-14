#!/usr/bin/env bash

source ../includes/02_helpers.sh

if [ -z "$1" ] || { [ "$1" != "enable" ] && [ "$1" != "disable" ]; }; then
    print_lc "Error: Invalid or no status provided.
Usage: ./static_ip.sh <status> <ipaddress>[optional]
       where <status> can be 'enable' or 'disable'"
    exit 1
fi

status="$1"

CURRENT_ROUTE=$(ip route get 8.8.8.8)
CURRENT_GATEWAY=$(echo "${CURRENT_ROUTE}" | awk '{ print $3; exit }')
CURRENT_INTERFACE=$(echo "${CURRENT_ROUTE}" | awk '{ print $5; exit }')
CURRENT_IP_ADDRESS=$(echo "${CURRENT_ROUTE}" | awk '{ print $7; exit }')
ipaddress="${1:-$CURRENT_IP_ADDRESS}" # No IP address provided, use current IP address

# DHCP
DHCP_CONF_PATH="/etc/dhcpcd.conf"
START_MARKER="## Jukebox DHCP Config Start"
END_MARKER="## Jukebox DHCP Config End"

_set_static_ip_dhcp() {
    local ipaddress="$1"

    # Check static IP has not been set
    if grep -q "${START_MARKER}" "$DHCP_CONF_PATH"; then
        _remove_static_ip
    fi

    log "${CURRENT_INTERFACE} is the default network interface"
    log "${CURRENT_GATEWAY} is the Router Gateway address"
    log "Using ${ipaddress} as the static IP"

    sudo tee -a $DHCP_CONF_PATH <<-EOF
${START_MARKER}
interface ${CURRENT_INTERFACE}
static ip_address=${ipaddress}/24
static routers=${CURRENT_GATEWAY}
static domain_name_servers=${CURRENT_GATEWAY}
noarp
${END_MARKER}
EOF
}

_remove_static_ip_dhcp() {
    sed -i "/$START_MARKER/,/$END_MARKER/d" "$DHCP_CONF_PATH"
}

# NetworkManager
get_nm_active_profile()
{
	local active_profile=$(nmcli -g DEVICE,CONNECTION device status | grep "^${CURRENT_INTERFACE}" | cut -d':' -f2)
	echo "$active_profile"
}

_set_static_ip_NetworkManager() {
    local ipaddress="$1"

    if [[ $(is_NetworkManager_enabled) == true ]]; then
        log "${CURRENT_INTERFACE} is the default network interface"
        log "${CURRENT_GATEWAY} is the Router Gateway address"
        log "Using ${ipaddress} as the static IP"
        local active_profile=$(get_nm_active_profile)
        sudo nmcli connection modify "$active_profile" ipv4.method manual ipv4.address "${ipaddress}/24" ipv4.gateway "$CURRENT_GATEWAY" ipv4.dns "$CURRENT_GATEWAY"
    fi
}

_remove_static_ip_NetworkManager() {
    # for future deactivation
    #sudo nmcli connection modify "$active_profile" ipv4.method auto ipv4.address "" ipv4.gateway "" ipv4.dns ""
    print_lc "Currently not implemented"
}


# Logic
if [ "$status" = "enable" ]; then
    print_lc "Enabling Static IP..."
elif [ "$status" = "disable" ]; then
    print_lc "Disabling Static IP..."
fi


if [[ $(is_dhcpcd_enabled) == true ]]; then
    cp "$DHCP_CONF_PATH" "${DHCP_CONF_PATH}.bak"

    if [ "$status" = "enable" ]; then
        _set_static_ip_dhcp "$ipaddress"
    elif [ "$status" = "disable" ]; then
        _remove_static_ip_dhcp
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

elif [[ $(is_NetworkManager_enabled) == true ]]; then
    if [ "$status" = "enable" ]; then
        _set_static_ip_NetworkManager "$ipaddress"
    elif [ "$status" = "disable" ]; then
        _remove_static_ip_NetworkManager
    fi

    # Test
    if [ "$status" = "enable" ]; then
        active_profile=$(get_nm_active_profile)
        active_profile_path="/etc/NetworkManager/system-connections/${active_profile}.nmconnection"
        verify_files_exists "${active_profile_path}"
        verify_file_contains_string "${ipaddress}" "${active_profile_path}"
        verify_file_contains_string "${CURRENT_GATEWAY}" "${active_profile_path}"
    elif [ "$status" = "disable" ]; then
        # TODO: Implement tests for disablement
    fi

else
    print_lc "No network service enabled. Aborting!"
fi
