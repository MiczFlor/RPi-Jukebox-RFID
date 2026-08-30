install() {
  clear_c
  # Only prompt for options in interactive mode. In non-interactive mode
  # (--config / --non-interactive) the options are supplied via a flat
  # KEY=VALUE config file or environment variables.
  if [[ "${NON_INTERACTIVE:-}" != "true" ]]; then
      customize_options
  else
      # Enforce option consistency and re-run the WebApp bundle normalization
      # that customize_options() would otherwise apply.
      if [[ "$ENABLE_WEBAPP" != "true" ]]; then
          ENABLE_KIOSK_MODE=false        # Kiosk mode requires the WebApp
      fi
      if [[ "$ENABLE_AUTOHOTSPOT" == "true" ]]; then
          ENABLE_STATIC_IP=false         # Autohotspot excludes static IP
      fi
      if [[ "$ENABLE_WEBAPP" == "true" ]]; then
          _configure_webapp_bundle_download
      fi
  fi
  clear_c
  show_slow_hardware_message
  prepare_dependencies
  set_raspi_config
  init_git_repo_from_tardir
  setup_jukebox_core
  setup_mpd
  setup_samba
  setup_jukebox_webapp
  # Audio HAT overlay — only when a board was selected. setup_hifiberry.sh
  # already supports non-interactive 'enable <board>'.
  if [[ -n "${HIFIBERRY_BOARD}" ]]; then
      (cd "${INSTALLATION_PATH}/installation/components" && \
          run_and_print_lc ./setup_hifiberry.sh enable "${HIFIBERRY_BOARD}")
  fi
  setup_kiosk_mode
  setup_rfid_reader
  optimize_boot_time
  setup_autohotspot
  setup_postinstall
  cleanup
}
