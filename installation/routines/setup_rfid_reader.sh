#!/usr/bin/env bash

_run_setup_rfid_reader() {
    local script="${INSTALLATION_PATH}"/installation/components/setup_rfid_reader.sh
    local args=()

    # Non-interactive: forward the selected reader module so that
    # run_register_rfid_reader.py does not present the reader menu. Readers
    # that need device/pin selection (e.g. generic_usb, rc522_spi) configure
    # themselves from the supplied RFID_READER_PARAMS or from their automatic
    # defaults (auto-detection); they abort with a clear error when no safe
    # default exists. In interactive mode the module is chosen later inside
    # the tool itself (no args -> interactive).
    #
    # Dependency handling is controlled by RFID_READER_DEPS ('auto' installs
    # the reader's requirements.txt and setup.inc.sh, 'no' skips them; the
    # config validation rejects 'query' in non-interactive mode because it
    # would prompt).
    if [[ "${NON_INTERACTIVE:-}" == "true" ]]; then
        if [[ -n "${RFID_READER_MODULE}" ]]; then
            args+=(--reader "${RFID_READER_MODULE}" --deps "${RFID_READER_DEPS:-auto}" --force)
            if [[ -n "${RFID_READER_PARAMS:-}" ]]; then
                args+=(--params "${RFID_READER_PARAMS}")
            fi
        else
            log "ERROR: ENABLE_RFID_READER=true but RFID_READER_MODULE is empty"
            exit_on_error "RFID reader is enabled but no reader module was selected."
        fi
    fi

    sudo chmod +x "$script"
    # run_and_print_lc propagates the tool's exit code (see install-jukebox.sh).
    # A failing reader configuration must abort the installation instead of
    # silently continuing with an unconfigured reader (broken daemon startup).
    if [[ "${#args[@]}" -gt 0 ]]; then
        run_and_print_lc "$script" "${args[@]}" \
            || exit_on_error "RFID reader configuration failed. See the install log for details."
    else
        run_and_print_lc "$script" \
            || exit_on_error "RFID reader configuration failed. See the install log for details."
    fi
}

setup_rfid_reader() {
    if [ "$ENABLE_RFID_READER" == true ] ; then
        run_with_log_frame _run_setup_rfid_reader "Install RFID Reader"
    fi
}
