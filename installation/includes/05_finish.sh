#!/usr/bin/env bash

finish() {
  echo -e "
---

Installation complete!

${FIN_MESSAGE}

In order to start, you need to reboot your Raspberry Pi.
Your SSH connection will disconnect.

After the reboot, open either http://raspberrypi.local
(for Mac / iOS) or http://[IP-ADDRESS] (for Android / Windows)
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

# Generic emergency error handler that exits the script immediately
# Print additional custom message if passed as first argument
# Examples:
#   cd some-dir || exit_on_error
#   cd some-dir || exit_on_error "During installation of some"
exit_on_error () {

  echo -e "\n****************************************" | tee /dev/fd/3
  echo -e "ERROR OCCURRED!
A non-recoverable error occurred.
Check install log for details:" | tee /dev/fd/3
  echo "$INSTALLATION_LOGFILE" | tee /dev/fd/3
  echo -e "****************************************" | tee /dev/fd/3
  if [[ -n $1 ]]; then
    echo "$1" | tee /dev/fd/3
    echo -e "****************************************" | tee /dev/fd/3
  fi
  echo "Abort!"
  exit 1
}
