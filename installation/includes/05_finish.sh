#!/usr/bin/env bash

finish() {
  echo "
---

Installation complete!

In order to start, you need to reboot your Raspberry Pi.
Your SSH connection will disconnect.

After the reboot, open either http://raspberrypi.local
(for Mac / iOS) or http://raspberrypi (for Android / Windows)
in a browser to get started. Don't forget to upload files
via Samba.

Do you want to reboot now? [Y/n]" 1>&3

  read -rp "Do you want to reboot now? [Y/n] " response
  case "$response" in
    [nN][oO]|[nN])
      echo "Reboot aborted" | tee /dev/fd/3
      echo "DONE: finish"
      exit
      ;;
    *)
      echo "Rebooting ..." | tee /dev/fd/3
      echo "DONE: finish"
      sudo reboot
      ;;
  esac
}
