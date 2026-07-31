#!/usr/bin/env bash

APT_PACKAGES=()

_add_apt_packages() {
    local package
    local existing
    local found

    for package in "$@"; do
        found=false
        for existing in "${APT_PACKAGES[@]}"; do
            if [[ "$existing" == "$package" ]]; then
                found=true
                break
            fi
        done
        if [[ "$found" == false ]]; then
            APT_PACKAGES+=("$package")
        fi
    done
}

_collect_apt_packages() {
    APT_PACKAGES=()

    local core_packages
    core_packages=($(get_args_from_file "${INSTALLATION_PATH}/packages-core.txt"))
    _add_apt_packages git "${core_packages[@]}"

    if [[ "$SETUP_MPD" == true && "$ENABLE_MPD_OVERWRITE_INSTALL" == true ]]; then
        _add_apt_packages mpd mpc
    fi

    if [[ "$ENABLE_SAMBA" == true ]]; then
        _add_apt_packages samba samba-common-bin
    fi

    if [[ "$ENABLE_WEBAPP" == true ]]; then
        # A trailing '-' asks APT to remove Apache in the same transaction.
        _add_apt_packages nginx apache2-

        if [[ "$ENABLE_WEBAPP_PROD_DOWNLOAD" == false && "$(get_architecture)" != "armv6" ]]; then
            _add_apt_packages nodejs npm
        fi
    fi

    if [[ "$ENABLE_KIOSK_MODE" == true ]]; then
        _add_apt_packages xserver-xorg x11-xserver-utils xinit openbox \
            "${KIOSK_MODE_CHROMIUM_PACKAGE}"
    fi

    if [[ "$ENABLE_AUTOHOTSPOT" == true ]]; then
        _add_apt_packages iw
        if [[ "$(is_dhcpcd_enabled)" == true || "$CI_RUNNING" == true ]]; then
            _add_apt_packages hostapd dnsmasq
        fi
    fi
}

_run_prepare_dependencies() {
    _collect_apt_packages

    if [[ "$ENABLE_SAMBA" == true ]]; then
        # Skip the interactive Samba WINS configuration dialog.
        echo "samba-common samba-common/dhcp boolean false" | sudo debconf-set-selections
    fi

    log "  Refresh package indexes"
    sudo apt-get -qq -y update || exit_on_error "Failed to refresh package indexes"

    update_raspi_os

    if [[ "$SETUP_MPD" == true && "$ENABLE_MPD_OVERWRITE_INSTALL" == true ]]; then
        log "Note: Installing MPD might cause a message: 'Job failed. See journalctl -xe for details'
It can be ignored! It's an artefact of the MPD installation - nothing we can do about it."
    fi

    log "  Install OS dependencies: ${APT_PACKAGES[*]}"
    sudo apt-get -y install \
        --no-install-recommends \
        --allow-downgrades \
        --allow-remove-essential \
        --allow-change-held-packages \
        "${APT_PACKAGES[@]}" || exit_on_error "Failed to install OS dependencies"
}

prepare_dependencies() {
    run_with_log_frame _run_prepare_dependencies "Prepare OS dependencies"
}
