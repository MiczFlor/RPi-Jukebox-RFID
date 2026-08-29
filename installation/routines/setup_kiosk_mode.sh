#!/usr/bin/env bash

KIOSK_MODE_CONF_HEADER="## Jukebox Kiosk Mode"
KIOSK_MODE_OPENBOX_AUTOSTART='/etc/xdg/openbox/autostart'
# The kiosk shell session belongs to the user that gets the console autologin
# (set by set_raspi_config via `raspi-config ... do_boot_behaviour B2`) — not
# necessarily the user running the installer. _kiosk_mode_set_autostart()
# resolves the real user and rewrites the per-user paths below accordingly.
KIOSK_MODE_USER="${CURRENT_USER:-$(whoami)}"
KIOSK_MODE_BASHRC="${HOME_PATH}/.bashrc"
KIOSK_MODE_XINITRC_FILE="${HOME_PATH}/.xinitrc"
KIOSK_MODE_CHROMIUM_FLAG_UPDATE_INTERVAL='--check-for-update-interval=31536000'

if [[ "$(get_architecture)" == "x86_64" ]] || [[ "$(is_debian_version_at_least 13)" == "true" ]]; then
    # Modern Debian (Trixie, 13+) and non-Debian x86_64 ship the browser as
    # plain 'chromium' and read its flags from /etc/chromium.d/. The
    # transitional 'chromium-browser' wrapper only exists on older images.
    KIOSK_MODE_CHROMIUM_PACKAGE='chromium'
    KIOSK_MODE_CHROMIUM_CUSTOM_DISABLE_UPDATE_CHECK='/etc/chromium.d/01-disable-update-check'
else
    # Legacy images (e.g. Raspberry Pi OS Bookworm) still use the
    # 'chromium-browser' transitional package and customizations path.
    KIOSK_MODE_CHROMIUM_PACKAGE='chromium-browser'
    KIOSK_MODE_CHROMIUM_CUSTOM_DISABLE_UPDATE_CHECK='/etc/chromium-browser/customizations/01-disable-update-check'
fi

# Determine the user the console autologin will log in (getty@tty1 drop-in
# written by `raspi-config nonint do_boot_behaviour B2`). Falls back to the
# user running the installer when no autologin is configured.
_get_kiosk_user() {
    local autologin_conf="/etc/systemd/system/getty@tty1.service.d/autologin.conf"
    local kiosk_user="${CURRENT_USER:-$(whoami)}"

    if [[ -r "${autologin_conf}" ]]; then
        local autologin_user
        autologin_user=$(sed -n 's/.*--autologin[[:space:]=]\([^[:space:]]*\).*/\1/p' "${autologin_conf}" | head -n1)
        if [[ -n "${autologin_user}" ]]; then
            kiosk_user="${autologin_user}"
        fi
    fi
    echo "${kiosk_user}"
}

# Resolve the actual chromium executable after the packages have been
# installed (the apt install runs in prepare_dependencies, before the kiosk
# setup). Modern releases provide plain 'chromium'; older images additionally
# ship the transitional 'chromium-browser' wrapper.
_get_chromium_command() {
    if command -v chromium >/dev/null 2>&1; then
        echo "chromium"
    elif command -v chromium-browser >/dev/null 2>&1; then
        echo "chromium-browser"
    else
        exit_on_error "Could not find a chromium executable after installation"
    fi
}

# Run a command either directly (install user == kiosk user), as the kiosk
# user (files in their home must keep the right ownership), or with sudo
# (system-wide files below /etc).
_kiosk_mode_run() {
    local file="$1"
    shift
    if [[ "${file}" == /etc/* ]]; then
        sudo "$@"
    elif [[ "$(whoami)" == "${KIOSK_MODE_USER}" ]]; then
        "$@"
    else
        sudo -u "${KIOSK_MODE_USER}" "$@"
    fi
}

# Remove previously inserted kiosk blocks. The blocks are always appended at
# the end of the target files, so deleting from the first header line to EOF
# removes all kiosk content and keeps re-running the installer idempotent.
_kiosk_mode_strip_blocks() {
    local file="$1"
    if [[ -f "${file}" ]]; then
        _kiosk_mode_run "${file}" sed -i "/^${KIOSK_MODE_CONF_HEADER}$/,\$d" "${file}"
    fi
}


_kiosk_mode_set_autostart() {
  print_lc "  Configure Kiosk Mode"
  local _DISPLAY='$DISPLAY'
  local _XDG_VTNR='$XDG_VTNR'
  local kiosk_home

  KIOSK_MODE_USER=$(_get_kiosk_user)
  kiosk_home=$(getent passwd "${KIOSK_MODE_USER}" | cut -d: -f6)
  if [[ -z "${kiosk_home}" ]]; then
      KIOSK_MODE_USER="${CURRENT_USER:-$(whoami)}"
      kiosk_home="${HOME_PATH}"
  fi
  KIOSK_MODE_BASHRC="${kiosk_home}/.bashrc"
  KIOSK_MODE_XINITRC_FILE="${kiosk_home}/.xinitrc"

  KIOSK_MODE_CHROMIUM_COMMAND=$(_get_chromium_command)

  _kiosk_mode_strip_blocks "${KIOSK_MODE_BASHRC}"
  _kiosk_mode_strip_blocks "${KIOSK_MODE_OPENBOX_AUTOSTART}"

  # Start the X server from the console login shell on VT 1.
  _kiosk_mode_run "${KIOSK_MODE_BASHRC}" tee -a "${KIOSK_MODE_BASHRC}" <<-EOF

${KIOSK_MODE_CONF_HEADER}
[[ -z $_DISPLAY && $_XDG_VTNR -eq 1 ]] && startx -- -nocursor

EOF

  # Make `startx` actually launch openbox (which reads the autostart file
  # below). Without this per-user .xinitrc the default Debian Xsession would
  # not start openbox and Chromium would never appear on the display.
  _kiosk_mode_run "${KIOSK_MODE_XINITRC_FILE}" tee "${KIOSK_MODE_XINITRC_FILE}" <<-EOF
#!/usr/bin/env sh
${KIOSK_MODE_CONF_HEADER}
exec openbox-session

EOF
  _kiosk_mode_run "${KIOSK_MODE_XINITRC_FILE}" chmod +x "${KIOSK_MODE_XINITRC_FILE}"

  # openbox system-wide autostart: keep the display alive and start Chromium.
  _kiosk_mode_run "${KIOSK_MODE_OPENBOX_AUTOSTART}" tee -a "${KIOSK_MODE_OPENBOX_AUTOSTART}" <<-EOF

${KIOSK_MODE_CONF_HEADER}
# Disable any form of screen saver / screen blanking / power management
xset s off
xset s noblank
xset -dpms

# Start Chromium in kiosk mode
sed -i 's/"exited_cleanly":false/"exited_cleanly":true/' ~/.config/chromium/'Local State'
sed -i 's/"exited_cleanly":false/"exited_cleanly":true/; s/"exit_type":"[^"]\+"/"exit_type":"Normal"/' ~/.config/chromium/Default/Preferences
${KIOSK_MODE_CHROMIUM_COMMAND} http://localhost \
  --disable-infobars \
  --disable-pinch \
  --disable-translate \
  --kiosk \
  --noerrdialogs \
  --no-first-run

EOF
}

_kiosk_mode_update_settings() {
  # Resource: https://github.com/Thyraz/Sonos-Kids-Controller/blob/d1f061f4662c54ae9b8dc8b545f9c3ba39f670eb/README.md#kiosk-mode-installation
  sudo mkdir -p "$(dirname "${KIOSK_MODE_CHROMIUM_CUSTOM_DISABLE_UPDATE_CHECK}")"
  sudo rm -f "${KIOSK_MODE_CHROMIUM_CUSTOM_DISABLE_UPDATE_CHECK}"
  sudo tee -a "${KIOSK_MODE_CHROMIUM_CUSTOM_DISABLE_UPDATE_CHECK}" <<-EOF
${KIOSK_MODE_CONF_HEADER}
CHROMIUM_FLAGS="\${CHROMIUM_FLAGS} ${KIOSK_MODE_CHROMIUM_FLAG_UPDATE_INTERVAL}"
EOF
}

_kiosk_mode_check() {
    print_verify_installation

    verify_apt_packages xserver-xorg \
        x11-xserver-utils \
        xinit \
        openbox \
        "${KIOSK_MODE_CHROMIUM_PACKAGE}"

    verify_commands_exists "${KIOSK_MODE_CHROMIUM_COMMAND}"

    verify_files_exists "${KIOSK_MODE_BASHRC}"
    verify_file_contains_string_once "${KIOSK_MODE_CONF_HEADER}" "${KIOSK_MODE_BASHRC}"

    verify_files_exists "${KIOSK_MODE_XINITRC_FILE}"
    verify_file_contains_string "exec openbox-session" "${KIOSK_MODE_XINITRC_FILE}"

    verify_files_exists "${KIOSK_MODE_OPENBOX_AUTOSTART}"
    verify_file_contains_string_once "${KIOSK_MODE_CONF_HEADER}" "${KIOSK_MODE_OPENBOX_AUTOSTART}"

    verify_files_exists "${KIOSK_MODE_CHROMIUM_CUSTOM_DISABLE_UPDATE_CHECK}"
    verify_file_contains_string "${KIOSK_MODE_CONF_HEADER}" "${KIOSK_MODE_CHROMIUM_CUSTOM_DISABLE_UPDATE_CHECK}"
}

_run_setup_kiosk_mode() {
    _kiosk_mode_set_autostart
    _kiosk_mode_update_settings
    _kiosk_mode_check
}


setup_kiosk_mode() {
    if [ "$ENABLE_KIOSK_MODE" == true ] ; then
        run_with_log_frame _run_setup_kiosk_mode "Setup Kiosk Mode"
    fi
}

