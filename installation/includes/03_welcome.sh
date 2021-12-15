#!/usr/bin/env bash

welcome() {
  clear 1>&3
  echo "#########################################################
#                                                       #
#      ___  __ ______  _  __________ ____   __  _  _    #
#     / _ \/ // / __ \/ |/ /  _/ __/(  _ \ /  \( \/ )   #
#    / ___/ _  / /_/ /    // // _/   ) _ ((  O ))  (    #
#   /_/  /_//_/\____/_/|_/___/____/ (____/ \__/(_/\_)   #
#   future3                                             #
#                                                       #
#########################################################

You are turning your Raspberry Pi into a Phoniebox.
Good choice!

Depending on your hardware, this installation might last
around 60 minutes. It updates OS packages, installs
Phoniebox dependencies and registers settings. Be patient
and don't let your computer go to sleep. It might
disconnect your SSH connection causing the interruption of
the installation process.

By the way, we write a log file to:
${INSTALLATION_LOGFILE}

Let's set up your Phoniebox now?! [Y/n]" 1>&3

  read -rp "Do you want to install? [Y/n] " response
  case "$response" in
    [nN][oO]|[nN])
      exit
      ;;
    *)
      echo "Starting installation
---------------------
" 1>&3
      ;;
  esac
}
