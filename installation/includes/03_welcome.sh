#!/usr/bin/env bash

welcome() {
  clear_c
  print_c "#########################################################
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
around 60 minutes (usually it's faster, 20-30 min). It
updates OS packages, installs Phoniebox dependencies and
applies settings. Be patient and don't let your computer
go to sleep. It might disconnect your SSH connection
causing the interruption of the installation process.
Consider starting the installation in a terminal
multiplexer like 'screen' or 'tmux' to avoid this.

To follow the installation closely, use this command
in another terminal.
cd; tail -f ${INSTALLATION_LOGFILE}

Let's set up your Phoniebox.
Do you want to start the installation? [Y/n]"
  read -r response
  case "$response" in
    [nN][oO]|[nN])
      exit
      ;;
    *)
      print_c "Starting installation
---------------------
"
      ;;
  esac
}
