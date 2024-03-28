is_raspbian() {
    if [[ $( . /etc/os-release; printf '%s\n' "$ID"; ) == *"raspbian"* ]]; then
        echo true
    else
        echo false
    fi
}

get_debian_version_number() {
    source /etc/os-release
    echo "$VERSION_ID"
}

_get_boot_file_path() {
    local filename="$1"
    if [ "$(is_raspbian)" = true ]; then
        local debian_version_number=$(get_debian_version_number)

        # Bullseye and lower
        if [ "$debian_version_number" -le 11 ]; then
            echo "/boot/${filename}"
        # Bookworm and higher
        elif [ "$debian_version_number" -ge 12 ]; then
            echo "/boot/firmware/${filename}"
        else
            echo "unknown"
        fi
    else
        echo "unknown"
    fi
}

get_boot_config_path() {
    echo $(_get_boot_file_path "config.txt")
}