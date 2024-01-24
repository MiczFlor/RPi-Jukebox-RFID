install() {
  clear_c
  customize_options
  clear_c
  show_slow_hardware_message
  update_raspi_os
  init_git_repo_from_tardir
  setup_jukebox_core
  setup_mpd
  setup_samba
  setup_jukebox_webapp
  setup_kiosk_mode
  setup_rfid_reader
  optimized_defaults
  setup_autohotspot
  cleanup
}
