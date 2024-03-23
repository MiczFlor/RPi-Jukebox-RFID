#!/usr/bin/env bash
source ../includes/00_constants.sh
source ../includes/02_helpers.sh

if [ -z "$1" ] || { [ "$1" != "enable" ] && [ "$1" != "disable" ]; }; then
    print_lc "Error: Invalid or no argument provided.
Usage: ./ipv6.sh <arg>
       where <arg> can be 'enable' or 'disable'"
    exit 1
fi

arg="$1"
cmdlineFile=$(get_boot_cmdline_path)
OPTIONS_IPV6="ipv6.disable=1"
nginx_is_installed=$(is_package_installed nginx)

if [ "$arg" = "enable" ]; then
    print_lc "Enabling IPv6..."
    _remove_options_to_cmdline "${OPTIONS_IPV6}"

    if [ "$nginx_is_installed" = "true" ]; then
        if ! grep -q 'listen \[::\]:80' "${WEBAPP_NGINX_SITE_DEFAULT_CONF}"; then
            echo 'listen [::]:80' | sudo tee -a "${WEBAPP_NGINX_SITE_DEFAULT_CONF}" > /dev/null
        fi
    fi

elif [ "$arg" = "disable" ]; then
    print_lc "Disabling IPv6..."
    _add_options_to_cmdline "${OPTIONS_IPV6}"

    if [ "$nginx_is_installed" = "true" ]; then
        sudo sed -i '/listen \[::\]:80/d' "${WEBAPP_NGINX_SITE_DEFAULT_CONF}"
    fi
fi

# Test
if [ "$arg" = "enable" ]; then
    verify_file_does_not_contain_string "${OPTIONS_IPV6}" "${cmdlineFile}"
    if [ "$nginx_is_installed" = "true" ]; then
        verify_file_contains_string "listen [::]:80" "${WEBAPP_NGINX_SITE_DEFAULT_CONF}"
    fi
elif [ "$arg" = "disable" ]; then
    verify_file_contains_string_once "${OPTIONS_IPV6}" "${cmdlineFile}"
    if [ "$nginx_is_installed" = "true" ]; then
        verify_file_does_not_contain_string "listen [::]:80" "${WEBAPP_NGINX_SITE_DEFAULT_CONF}"
    fi
fi
