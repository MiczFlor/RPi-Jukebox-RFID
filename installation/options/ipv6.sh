#!/usr/bin/env bash
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

if [ "$arg" = "enable" ]; then
    print_lc "Enabling IPv6..."
    _remove_options_to_cmdline "${OPTIONS_IPV6}" # TODO implement _remove_options_to_cmdline
elif [ "$arg" = "disable" ]; then
    print_lc "Disabling IPv6..."
    _add_options_to_cmdline "${OPTIONS_IPV6}"
fi

# Test
if [ "$arg" = "enable" ]; then
    verify_file_does_not_contain_string "${OPTIONS_IPV6}" "${cmdlineFile}"
elif [ "$arg" = "disable" ]; then
    verify_file_contains_string_once "${OPTIONS_IPV6}" "${cmdlineFile}"
fi
