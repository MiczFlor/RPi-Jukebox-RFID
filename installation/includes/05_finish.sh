#!/usr/bin/env bash

finish() {
local local_hostname=$(hostname)
  print_lc "####################### FINISHED ########################

Installation complete!

${FIN_MESSAGE}

In order to start, you need to reboot your Raspberry Pi.
Your SSH connection will disconnect.

After the reboot, you can access the WebApp in your browser at
http://${local_hostname}.local or http://${CURRENT_IP_ADDRESS}
Don't forget to upload files.
"
print_c "Do you want to reboot now? [Y/n]"

  read -r response
  case "$response" in
    [nN][oO]|[nN])
      print_lc "Reboot aborted"
      log "DONE: finish"
      exit
      ;;
    *)
      print_lc "Rebooting ..."
      log "DONE: finish"
      sudo reboot
      ;;
  esac
}
