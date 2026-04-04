#!/usr/bin/env bash

KIOSK_MODE_CONF_HEADER="## Jukebox Kiosk Mode"
KIOSK_MODE_XINITRC='/etc/xdg/openbox/autostart'
KIOSK_MODE_BASHRC="${HOME_PATH}/.bashrc"
KIOSK_MODE_BASH_PROFILE="${HOME_PATH}/.bash_profile"
KIOSK_MODE_LABWC_DIR="${HOME_PATH}/.config/labwc"
KIOSK_MODE_LABWC_AUTOSTART="${KIOSK_MODE_LABWC_DIR}/autostart"
KIOSK_MODE_CHROMIUM_CUSTOM_DISABLE_UPDATE_CHECK='/etc/chromium-browser/customizations/01-disable-update-check'
KIOSK_MODE_CHROMIUM_FLAG_UPDATE_INTERVAL='--check-for-update-interval=31536000'
KIOSK_MODE_BOOKWORM_DISPLAY_SCALE='1.35'

_kiosk_mode_use_bookworm_variant() {
  if [ "$(is_debian_version_at_least 12)" = true ] ; then
    echo true
  else
    echo false
  fi
}

_kiosk_mode_install_os_dependencies() {
  print_lc "  Install Kiosk Mode dependencies"
  if [ "$(_kiosk_mode_use_bookworm_variant)" = true ] ; then
    sudo apt-get -qq -y install --no-install-recommends \
      labwc \
      wlr-randr \
      fonts-noto-color-emoji \
      chromium-browser
  else
    # Resource:
    # https://blog.r0b.io/post/minimal-rpi-kiosk/
    sudo apt-get -qq -y install --no-install-recommends \
      xserver-xorg \
      x11-xserver-utils \
      xinit \
      openbox \
      fonts-noto-color-emoji \
      chromium-browser
  fi
}

_kiosk_mode_set_legacy_autostart() {
  local _DISPLAY='$DISPLAY'
  local _XDG_VTNR='$XDG_VTNR'

  tee -a "${KIOSK_MODE_BASHRC}" <<-EOF

${KIOSK_MODE_CONF_HEADER}
[[ -z $_DISPLAY && $_XDG_VTNR -eq 1 ]] && startx -- -nocursor

EOF

  sudo tee -a "${KIOSK_MODE_XINITRC}" <<-EOF

${KIOSK_MODE_CONF_HEADER}
# Disable any form of screen saver / screen blanking / power management
xset s off
xset s noblank
xset -dpms

# Start Chromium in kiosk mode
sed -i 's/"exited_cleanly":false/"exited_cleanly":true/' ~/.config/chromium/'Local State'
sed -i 's/"exited_cleanly":false/"exited_cleanly":true/; s/"exit_type":"[^"]\+"/"exit_type":"Normal"/' ~/.config/chromium/Default/Preferences
chromium-browser http://localhost \
  --disable-infobars \
  --disable-pinch \
  --disable-translate \
  --kiosk \
  --noerrdialogs \
  --no-first-run

EOF
}

_kiosk_mode_set_bookworm_autostart() {
  print_lc "  Configure Kiosk Mode for Bookworm"

  mkdir -p "${KIOSK_MODE_LABWC_DIR}"

  if [ ! -f "${KIOSK_MODE_BASH_PROFILE}" ] ; then
    tee "${KIOSK_MODE_BASH_PROFILE}" <<-EOF
if [ -f "\$HOME/.profile" ]; then
  . "\$HOME/.profile"
fi

EOF
  fi

  if ! grep -Fq "${KIOSK_MODE_CONF_HEADER}" "${KIOSK_MODE_BASH_PROFILE}" 2>/dev/null ; then
    tee -a "${KIOSK_MODE_BASH_PROFILE}" <<-EOF

${KIOSK_MODE_CONF_HEADER}
if [ -z "\$DISPLAY" ] && [ -z "\$WAYLAND_DISPLAY" ] && [ "\${XDG_VTNR:-0}" -eq 1 ] && command -v labwc >/dev/null 2>&1; then
  export XDG_SESSION_TYPE=wayland
  export MOZ_ENABLE_WAYLAND=1
  export WLR_NO_HARDWARE_CURSORS=1
  export WLR_RENDERER=pixman
  mkdir -p "\$HOME/.cache"
  echo "\$(date -Is) starting Bookworm kiosk" >> "\$HOME/.cache/phoniebox-kiosk-session.log"
  exec labwc >> "\$HOME/.cache/phoniebox-kiosk-session.log" 2>&1
fi

EOF
  fi

  tee "${KIOSK_MODE_LABWC_AUTOSTART}" <<-EOF
#!/usr/bin/env bash

${KIOSK_MODE_CONF_HEADER}
wlr-randr --output DSI-1 --on >/dev/null 2>&1 || true
(
  while ! wget -q --spider http://localhost; do
    sleep 1
  done

  chromium-browser http://localhost \\
    --enable-features=UseOzonePlatform \\
    --ozone-platform=wayland \\
    --disable-gpu \\
    --force-device-scale-factor=${KIOSK_MODE_BOOKWORM_DISPLAY_SCALE} \\
    --disable-infobars \\
    --disable-pinch \\
    --disable-translate \\
    --kiosk \\
    --noerrdialogs \\
    --no-first-run \\
    >> "\$HOME/.cache/phoniebox-kiosk-browser.log" 2>&1
) &
EOF

  chmod 755 "${KIOSK_MODE_LABWC_AUTOSTART}"
}

_kiosk_mode_set_autostart() {
  print_lc "  Configure Kiosk Mode"
  if [ "$(_kiosk_mode_use_bookworm_variant)" = true ] ; then
    _kiosk_mode_set_bookworm_autostart
  else
    _kiosk_mode_set_legacy_autostart
  fi
}

_kiosk_mode_update_settings() {
  # Resource: https://github.com/Thyraz/Sonos-Kids-Controller/blob/d1f061f4662c54ae9b8dc8b545f9c3ba39f670eb/README.md#kiosk-mode-installation
  sudo mkdir -p $(dirname "${KIOSK_MODE_CHROMIUM_CUSTOM_DISABLE_UPDATE_CHECK}")
  sudo rm -f "${KIOSK_MODE_CHROMIUM_CUSTOM_DISABLE_UPDATE_CHECK}"
  sudo tee -a "${KIOSK_MODE_CHROMIUM_CUSTOM_DISABLE_UPDATE_CHECK}" <<-EOF
${KIOSK_MODE_CONF_HEADER}
CHROMIUM_FLAGS=\"\$\{CHROMIUM_FLAGS\} --check-for-update-interval=31536000\"
EOF
}

_kiosk_mode_check() {
    print_verify_installation

    if [ "$(_kiosk_mode_use_bookworm_variant)" = true ] ; then
        verify_apt_packages labwc \
            wlr-randr \
            fonts-noto-color-emoji \
            chromium-browser

        verify_files_exists "${KIOSK_MODE_BASH_PROFILE}"
        verify_file_contains_string "${KIOSK_MODE_CONF_HEADER}" "${KIOSK_MODE_BASH_PROFILE}"
        verify_file_contains_string "labwc" "${KIOSK_MODE_BASH_PROFILE}"

        verify_files_exists "${KIOSK_MODE_LABWC_AUTOSTART}"
        verify_file_contains_string "${KIOSK_MODE_CONF_HEADER}" "${KIOSK_MODE_LABWC_AUTOSTART}"
        verify_file_contains_string "ozone-platform=wayland" "${KIOSK_MODE_LABWC_AUTOSTART}"
        verify_file_contains_string "force-device-scale-factor=${KIOSK_MODE_BOOKWORM_DISPLAY_SCALE}" "${KIOSK_MODE_LABWC_AUTOSTART}"
    else
        verify_apt_packages xserver-xorg \
            x11-xserver-utils \
            xinit \
            openbox \
            fonts-noto-color-emoji \
            chromium-browser

        verify_files_exists "${KIOSK_MODE_BASHRC}"
        verify_file_contains_string "${KIOSK_MODE_CONF_HEADER}" "${KIOSK_MODE_BASHRC}"

        verify_files_exists "${KIOSK_MODE_XINITRC}"
        verify_file_contains_string "${KIOSK_MODE_CONF_HEADER}" "${KIOSK_MODE_XINITRC}"
    fi

    verify_files_exists "${KIOSK_MODE_CHROMIUM_CUSTOM_DISABLE_UPDATE_CHECK}"
    verify_file_contains_string "${KIOSK_MODE_CONF_HEADER}" "${KIOSK_MODE_CHROMIUM_CUSTOM_DISABLE_UPDATE_CHECK}"
}

_run_setup_kiosk_mode() {
    _kiosk_mode_install_os_dependencies
    _kiosk_mode_set_autostart
    _kiosk_mode_update_settings
    _kiosk_mode_check
}


setup_kiosk_mode() {
    if [ "$ENABLE_KIOSK_MODE" == true ] ; then
        run_with_log_frame _run_setup_kiosk_mode "Setup Kiosk Mode"
    fi
}
