#!/usr/bin/env bash
source ../includes/02_helpers.sh
script_name=$(basename "$0")
boot_config_path=$(get_boot_config_path)

if [ -z "$1" ] || { [ "$1" != "enable" ] && [ "$1" != "disable" ]; }; then
    echo "Error: Invalid or no argument provided.
Usage: ./${script_name} <arg>
       where <arg> can be 'enable' or 'disable'"
    exit 1
fi

arg="$1"

if [ "$arg" = "enable" ]; then
    echo "Enabling Onboard Sound..."
    sudo sed -i '/dtoverlay=vc4-fkms-v3d,audio=off/c\dtoverlay=vc4-fkms-v3d' "$boot_config_path"
    sudo sed -i '/dtoverlay=vc4-kms-v3d,noaudio/c\dtoverlay=vc4-kms-v3d' "$boot_config_path"
elif [ "$arg" = "disable" ]; then
    echo "Disabling Onboard Sound..."
    sudo sed -i "s/^\(dtparam=\([^,]*,\)*\)audio=\(on\|true\|yes\|1\)\(.*\)/\1audio=off\4/g" "$boot_config_path"

    if grep -qx 'dtoverlay=vc4-fkms-v3d' "$boot_config_path"; then
        sudo sed -i '/dtoverlay=vc4-fkms-v3d/c\dtoverlay=vc4-fkms-v3d,audio=off' "$boot_config_path"
    fi

    if grep -qx 'dtoverlay=vc4-kms-v3d' "$boot_config_path"; then
        sudo sed -i '/dtoverlay=vc4-kms-v3d/c\dtoverlay=vc4-kms-v3d,noaudio' "$boot_config_path"
    fi
fi

# TODO Test
