install() {
  welcome
  customize_options
  clear 1>&3
  set_raspi_config
  if [ "$DISABLE_SSH_QOS" = true ] ; then set_ssh_qos; fi;
  if [ "$UPDATE_RASPI_OS" = true ] ; then update_raspi_os; fi;
  setup_jukebox_core
  if [ "$SETUP_MPD" = true ] ; then setup_mpd; fi;
  if [ "$ENABLE_SAMBA" = true ] ; then setup_samba; fi;
  if [ "$ENABLE_WEBAPP" = true ] ; then setup_jukebox_webapp; fi;
  if [ "$ENABLE_KIOSK_MODE" = true ] ; then setup_kiosk_mode; fi;
  setup_rfid_reader
  optimize_boot_time
  cleanup
  finish
}
