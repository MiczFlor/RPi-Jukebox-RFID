setup_autohotspot() {
    if [ "$ENABLE_AUTOHOTSPOT" == true ] ; then
        run_with_log_frame _run_setup_autohotspot_dhcpcd "Install AutoHotspot"
    fi
}
