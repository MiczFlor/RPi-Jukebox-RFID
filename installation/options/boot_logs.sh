#!/usr/bin/env bash
source ../includes/02_helpers.sh

if [ -z "$1" ] || { [ "$1" != "enable" ] && [ "$1" != "disable" ]; }; then
    print_lc "Error: Invalid or no argument provided.
Usage: ./boot_logs.sh <arg>
       where <arg> can be 'enable' or 'disable'"
    exit 1
fi

arg="$1"
boot_cmdline_path=$(get_boot_cmdline_path)
boot_cmdline_options="consoleblank=1 logo.nologo quiet loglevel=0 plymouth.enable=0 vt.global_cursor_default=0 plymouth.ignore-serial-consoles splash fastboot noatime nodiratime noram"

if [ "$arg" = "enable" ]; then
    print_lc "Enable Boot logs..."

    if [ -s "${boot_cmdline_path}" ]; then
        for option in $boot_cmdline_options; do
            sudo sed -i "s/\s*$option\s*/ /" "${boot_cmdline_path}"
        done
    fi
elif [ "$arg" = "disable" ]; then
    print_lc "Disable Boot logs..."

    if [ ! -s "${boot_cmdline_path}" ];then
        sudo tee "${boot_cmdline_path}" <<-EOF
${boot_cmdline_options}
EOF
    else
        for option in $boot_cmdline_options
        do
            if ! grep -qiw "$option" "${boot_cmdline_path}" ; then
                sudo sed -i "s/$/ $option/" "${boot_cmdline_path}"
            fi
        done
    fi
fi

# Test
if [ "$arg" = "enable" ]; then
    for option in $boot_cmdline_options
    do
        verify_file_does_not_contain_string $option "${boot_cmdline_path}"
    done
elif [ "$arg" = "disable" ]; then
    for option in $boot_cmdline_options
    do
        verify_file_contains_string_once $option "${boot_cmdline_path}"
    done
fi
