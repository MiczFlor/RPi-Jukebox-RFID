#!/usr/bin/env bash

_kiosk_mode_install_os_dependencies() {
  # Resource:
  # https://blog.r0b.io/post/minimal-rpi-kiosk/
  sudo apt-get -qq -y install --no-install-recommends \
    xserver-xorg \
    x11-xserver-utils \
    xinit \
    openbox \
    chromium-browser
}

_kiosk_mode_set_autostart() {
  local _DISPLAY='$DISPLAY'
  local _XDG_VTNR='$XDG_VTNR'
  cat << EOF >> /home/pi/.bashrc

## Jukebox kiosk autostart
[[ -z $_DISPLAY && $_XDG_VTNR -eq 1 ]] && startx -- -nocursor

EOF

  local XINITRC='/etc/xdg/openbox/autostart'
  cat << EOF | sudo tee -a $XINITRC

## Jukebox Kiosk Mode
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

_kiosk_mode_update_settings() {
  # Resource: https://github.com/Thyraz/Sonos-Kids-Controller/blob/d1f061f4662c54ae9b8dc8b545f9c3ba39f670eb/README.md#kiosk-mode-installation
  sudo touch /etc/chromium-browser/customizations/01-disable-update-check;echo CHROMIUM_FLAGS=\"\$\{CHROMIUM_FLAGS\} --check-for-update-interval=31536000\" | sudo tee /etc/chromium-browser/customizations/01-disable-update-check

}

setup_kiosk_mode() {
  echo "Setup Kiosk Mode" | tee /dev/fd/3

  _kiosk_mode_install_os_dependencies
  _kiosk_mode_set_autostart
  _kiosk_mode_update_settings

  echo "DONE: setup_kiosk_mode"
}
