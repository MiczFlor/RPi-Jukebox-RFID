_setup_login_message() {
    local login_message_welcome_file="/etc/update-motd.d/99-rpi-jukebox-rfid-welcome"
    sudo cp -f "${INSTALLATION_PATH}/resources/system/99-rpi-jukebox-rfid-welcome" "$login_message_welcome_file"
    sudo chmod +x "$login_message_welcome_file"
}

_run_setup_postinstall() {
    _setup_login_message
}

setup_postinstall() {
    run_with_log_frame _run_setup_postinstall "Post install"
}
