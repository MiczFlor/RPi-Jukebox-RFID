install() {
  clear_c
  customize_options
  clear_c
  set_raspi_config
  set_ssh_qos
  update_raspi_os
  init_git_repo_from_tardir
  setup_jukebox_core
  setup_mpd
  setup_samba
  setup_jukebox_webapp
  setup_kiosk_mode
  setup_rfid_reader
  optimize_boot_time
  setup_autohotspot
  cleanup
}
