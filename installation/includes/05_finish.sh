#!/usr/bin/env bash

finish() {
local local_hostname=$(hostname)
  echo -e "####################### FINISHED ########################

Installation complete!

${FIN_MESSAGE}

In order to start, you need to reboot your Raspberry Pi.
Your SSH connection will disconnect.

After the reboot, you can access the WebApp in your browser at
http://${local_hostname}.local or http://${CURRENT_IP_ADDRESS}
Don't forget to upload files.
" | tee /dev/fd/3
echo "Do you want to reboot now? [Y/n]" 1>&3

  read -r response
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
