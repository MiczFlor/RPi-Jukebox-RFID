#!/usr/bin/env bash

# documentation of spotifyd
# https://docs.spotifyd.rs/installation/Raspberry-Pi.html

SPOTIFYD_SERVICE_FILE="/etc/systemd/user/spotifyd.service"
SPOTIFYD_TAR="https://github.com/Spotifyd/spotifyd/releases/latest/download/spotifyd-linux-armhf-default.tar.gz"
SPOTIFYD_TAR_FILE_NAME="spotifyd.tar.gz"

SPOTIFYD_TARGET_PATH="/usr/bin/"
SPOTIFYD_TARGET_FILE="/usr/bin/spotifyd"
SPOTIFYD_CONFIG_TARGET_FILE="/etc/spotifyd.conf"


_install_spotifyd_script() {
    wget "${SPOTIFYD_TAR}" --output-document "${SPOTIFYD_TAR_FILE_NAME}"
    sudo tar xzf "${SPOTIFYD_TAR_FILE_NAME}" -C "${SPOTIFYD_TARGET_PATH}"

    # Cleanup
    # rm -f "${SPOTIFYD_TAR_FILE_NAME}"
}


_install_spotifyd_service() {
    sudo cp "${INSTALLATION_PATH}"/resources/default-services/spotifyd.service /etc/systemd/system/spotifyd.service
    sudo systemctl enable spotifyd.service
}

_configure_spotifyd() {
    local SPOTIFYD_CUSTOM_FILE="${INSTALLATION_PATH}"/resources/default-settings/spotifyd.default.conf

    sed -i "s/%%SPOT_USERNAME%%/${SPOT_USERNAME}/g" "${SPOTIFYD_CUSTOM_FILE}"
    sed -i "s/%%SPOT_PASSWORD%%/${SPOT_PASSWORD}/g" "${SPOTIFYD_CUSTOM_FILE}"
    sudo cp "${SPOTIFYD_CUSTOM_FILE}" "${SPOTIFYD_CONFIG_TARGET_FILE}"

}

_configure_spotipy() {
    local PLAYER_YAML_FILE="${SETTINGS_PATH}/player.yaml"

    sed -i "s/%%SPOT_CLIENT_ID%%/${SPOT_CLIENT_ID}/g" "${PLAYER_YAML_FILE}"
    sed -i "s/%%SPOT_CLIENT_SECRET%%/${SPOT_CLIENT_SECRET}/g" "${PLAYER_YAML_FILE}"

}


_spotifyd_check() {
    print_verify_installation

    verify_service_enablement spotifyd.service enabled

    verify_files_exists "${SPOTIFYD_TARGET_FILE}"

    verify_file_contains_string "${SPOT_USERNAME}" "${SPOTIFYD_CONFIG_TARGET_FILE}"
    verify_file_contains_string "${SPOT_PASSWORD}" "${SPOTIFYD_CONFIG_TARGET_FILE}"

}

_run_setup_spotifyd() {
    _install_spotifyd_script
    _install_spotifyd_service
    _configure_spotifyd
    _configure_spotipy
    _spotifyd_check
}

setup_spotifyd() {
    if [ "$ENABLE_SPOTIFY" == true ] ; then
        run_with_log_frame _run_setup_spotifyd "Install Spotifyd"
    fi
}
