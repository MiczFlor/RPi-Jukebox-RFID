#!/usr/bin/env bash

# Tests for the non-interactive installation support:
# - 01_default_config.sh must not overwrite values set via --config/env (E1).
# - _option_*() functions must skip their interactive prompts when
#   NON_INTERACTIVE=true.
# - The non-interactive code paths in the install scripts: config file
#   loading, fail-fast validation, existing-installation handling,
#   welcome/finish prompt skipping, install() option consistency and RFID
#   reader module/params forwarding.

set -euo pipefail

SOURCE="${BASH_SOURCE[0]}"
SCRIPT_DIR="$(dirname "$SOURCE")"
REPOSITORY_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"

# Stub the console/log helpers used by the installation routines
clear_c() { :; }
print_c() { :; }
log() { :; }
print_lc() { :; }

fail() {
    echo "ERROR: $*" >&2
    exit 1
}

# --- 01_default_config.sh must NOT overwrite pre-set values ---
ENABLE_STATIC_IP="false"
DISABLE_IPv6="false"
ENABLE_SAMBA="true"
ENABLE_RFID_READER="false"
ENABLE_WEBAPP="false"
DISABLE_BLUETOOTH="false"
source "${REPOSITORY_ROOT}/installation/includes/01_default_config.sh"
[[ "${ENABLE_STATIC_IP}" == "false" ]]
[[ "${DISABLE_IPv6}" == "false" ]]
[[ "${ENABLE_SAMBA}" == "true" ]]
[[ "${ENABLE_RFID_READER}" == "false" ]]
[[ "${ENABLE_WEBAPP}" == "false" ]]
[[ "${DISABLE_BLUETOOTH}" == "false" ]]

# Defaults still apply when a variable is unset
unset ENABLE_SAMBA
source "${REPOSITORY_ROOT}/installation/includes/01_default_config.sh"
[[ "${ENABLE_SAMBA}" == "false" ]]

# --- _option_*() skip prompts when NON_INTERACTIVE=true ---
source "${REPOSITORY_ROOT}/installation/routines/customize_options.sh"

NON_INTERACTIVE="true"

ENABLE_SAMBA="true"
_option_samba <<< ''
[[ "${ENABLE_SAMBA}" == "true" ]]   # untouched by the prompt

ENABLE_SAMBA="false"
_option_samba <<< 'y'
[[ "${ENABLE_SAMBA}" == "false" ]]  # still untouched

DISABLE_BLUETOOTH="false"
_option_bluetooth <<< ''
[[ "${DISABLE_BLUETOOTH}" == "false" ]]

ENABLE_WEBAPP="false"
_option_webapp <<< ''
[[ "${ENABLE_WEBAPP}" == "false" ]]

ENABLE_RFID_READER="false"
_option_rfid_reader <<< ''
[[ "${ENABLE_RFID_READER}" == "false" ]]

# --- _load_install_config(), _validate_noninteractive_config() and
#     _check_existing_installation() ---
# These functions are defined in install-jukebox.sh, which runs the actual
# installation when sourced directly. Extract only the function bodies.
source <(
    sed -n \
        -e '/^_load_install_config()/,/^}/p' \
        -e '/^_validate_noninteractive_config()/,/^}/p' \
        -e '/^_check_existing_installation()/,/^}/p' \
        "${REPOSITORY_ROOT}/installation/install-jukebox.sh"
)
declare -F _load_install_config >/dev/null || fail "could not extract _load_install_config"
declare -F _validate_noninteractive_config >/dev/null || fail "could not extract _validate_noninteractive_config"
declare -F _check_existing_installation >/dev/null || fail "could not extract _check_existing_installation"

TEST_ROOT=$(mktemp -d)
trap 'rm -rf "${TEST_ROOT}"' EXIT

GIT_REPO_NAME="RPi-Jukebox-RFID"
GIT_USER="MiczFlor"
GIT_BRANCH="future3/main"
GIT_URL="https://github.com/${GIT_USER}/${GIT_REPO_NAME}"

# A flat KEY=VALUE config file is sourced and enables non-interactive mode
INSTALL_CONFIG_FILE="${TEST_ROOT}/install_config.env"
cat > "${INSTALL_CONFIG_FILE}" <<'EOF'
GIT_USER="fork-user"
GIT_BRANCH="feature/test"
ENABLE_SAMBA=true
ENABLE_WEBAPP=true
EXISTING_INSTALL_ACTION=remove
EOF

_load_install_config
[[ "${NON_INTERACTIVE}" == "true" ]]          || fail "NON_INTERACTIVE was not enabled"
[[ "${GIT_USER}" == "fork-user" ]]            || fail "GIT_USER was not loaded from the config"
[[ "${GIT_BRANCH}" == "feature/test" ]]       || fail "GIT_BRANCH was not loaded from the config"
[[ "${GIT_URL}" == "https://github.com/fork-user/RPi-Jukebox-RFID" ]] \
    || fail "GIT_URL was not recomputed after the config override"
[[ "${ENABLE_SAMBA}" == "true" ]]             || fail "ENABLE_SAMBA was not loaded from the config"
[[ "${ENABLE_WEBAPP}" == "true" ]]            || fail "ENABLE_WEBAPP was not loaded from the config"

# A missing config file aborts
INSTALL_CONFIG_FILE="${TEST_ROOT}/missing.env"
if ( _load_install_config ) >/dev/null 2>&1; then
    fail "a missing config file was accepted"
fi
INSTALL_CONFIG_FILE=""

# Existing installation handling in non-interactive mode
INSTALLATION_PATH="${TEST_ROOT}/existing"
NON_INTERACTIVE=true

mkdir -p "${INSTALLATION_PATH}"
EXISTING_INSTALL_ACTION=remove
_check_existing_installation
[[ ! -e "${INSTALLATION_PATH}" ]] || fail "EXISTING_INSTALL_ACTION=remove did not delete the installation"

mkdir -p "${INSTALLATION_PATH}"
EXISTING_INSTALL_ACTION=backup
_check_existing_installation
[[ ! -e "${INSTALLATION_PATH}" ]] || fail "EXISTING_INSTALL_ACTION=backup did not move the installation"
[[ "$(find "${TEST_ROOT}" -maxdepth 1 -name 'existing.bak-*' | wc -l)" -eq 1 ]] \
    || fail "EXISTING_INSTALL_ACTION=backup did not create a backup directory"

mkdir -p "${INSTALLATION_PATH}"
EXISTING_INSTALL_ACTION=bogus
if ( _check_existing_installation ) >/dev/null 2>&1; then
    fail "an unknown EXISTING_INSTALL_ACTION was accepted"
fi

# The interactive flow keeps the hard abort
if ( NON_INTERACTIVE=false; _check_existing_installation ) >/dev/null 2>&1; then
    fail "an interactive rerun over an existing installation was accepted"
fi

# --- _validate_noninteractive_config() fails fast on a broken config ---
# ENABLE_RFID_READER is not set: the default (true) applies, so a missing
# RFID_READER_MODULE must abort before anything is installed.
NON_INTERACTIVE=true
unset ENABLE_RFID_READER RFID_READER_MODULE
if ( _validate_noninteractive_config ) >/dev/null 2>&1; then
    fail "a non-interactive config without RFID_READER_MODULE was accepted"
fi

# Explicitly enabled reader without a module aborts as well
ENABLE_RFID_READER=true
if ( _validate_noninteractive_config ) >/dev/null 2>&1; then
    fail "ENABLE_RFID_READER=true without RFID_READER_MODULE was accepted"
fi

# A disabled reader or a configured module pass the validation
ENABLE_RFID_READER=false
_validate_noninteractive_config

ENABLE_RFID_READER=true
RFID_READER_MODULE="pn532_i2c_py532"
_validate_noninteractive_config

# RFID_READER_DEPS accepts only 'auto'/'no' in non-interactive mode;
# 'query' would prompt and must be rejected
RFID_READER_DEPS="no"
_validate_noninteractive_config
RFID_READER_DEPS="query"
if ( _validate_noninteractive_config ) >/dev/null 2>&1; then
    fail "RFID_READER_DEPS=query was accepted in non-interactive mode"
fi
unset RFID_READER_DEPS
_validate_noninteractive_config

# Interactive mode is not affected by the non-interactive validation
unset ENABLE_RFID_READER RFID_READER_MODULE
NON_INTERACTIVE=false
_validate_noninteractive_config

# --- welcome() and finish() must not prompt in non-interactive mode ---
source "${REPOSITORY_ROOT}/installation/includes/03_welcome.sh"
source "${REPOSITORY_ROOT}/installation/includes/05_finish.sh"

CAPTURED=()
print_c() { CAPTURED+=("$1"); }
print_lc() { CAPTURED+=("$1"); }

read() {
    fail "read was called in non-interactive mode"
}
sudo() {
    fail "sudo was called in non-interactive mode"
}

NON_INTERACTIVE=true
INSTALLATION_LOGFILE="${TEST_ROOT}/install.log"
FIN_MESSAGE=""
CURRENT_IP_ADDRESS="127.0.0.1"

welcome
[[ "${CAPTURED[${#CAPTURED[@]}-1]}" == *"Starting installation"* ]] \
    || fail "welcome did not continue in non-interactive mode"

CAPTURED=()
finish
[[ "${CAPTURED[${#CAPTURED[@]}-1]}" == *"Reboot skipped (non-interactive mode)"* ]] \
    || fail "finish did not report the skipped reboot"

unset -f read sudo print_c print_lc
print_c() { :; }
print_lc() { :; }

# --- _run_setup_rfid_reader() forwards the module in non-interactive mode ---
source "${REPOSITORY_ROOT}/installation/routines/setup_rfid_reader.sh"

INSTALLATION_PATH="${TEST_ROOT}"
RFID_SCRIPT="${INSTALLATION_PATH}/installation/components/setup_rfid_reader.sh"
mkdir -p "$(dirname "${RFID_SCRIPT}")"
echo '#!/usr/bin/env bash' > "${RFID_SCRIPT}"

RUN_ARGS=()
run_and_print_lc() { RUN_ARGS+=("$*"); }
sudo() { :; }
exit_on_error() { echo "$*" >&2; exit 1; }

NON_INTERACTIVE=true
RFID_READER_MODULE="pn532_i2c_py532"
_run_setup_rfid_reader
[[ "${RUN_ARGS[${#RUN_ARGS[@]}-1]}" == "${RFID_SCRIPT} --reader pn532_i2c_py532 --deps auto --force" ]] \
    || fail "RFID reader module was not forwarded in non-interactive mode"

# RFID_READER_PARAMS are forwarded to the reader configuration tool
RFID_READER_MODULE="rc522_spi"
RFID_READER_PARAMS="spi_ce=0;pin_irq=24"
RUN_ARGS=()
_run_setup_rfid_reader
[[ "${RUN_ARGS[${#RUN_ARGS[@]}-1]}" == "${RFID_SCRIPT} --reader rc522_spi --deps auto --force --params spi_ce=0;pin_irq=24" ]] \
    || fail "RFID_READER_PARAMS were not forwarded in non-interactive mode"
unset RFID_READER_PARAMS

# RFID_READER_DEPS controls the dependency handling ('no' skips deps)
RFID_READER_MODULE="pn532_i2c_py532"
RFID_READER_DEPS="no"
RUN_ARGS=()
_run_setup_rfid_reader
[[ "${RUN_ARGS[${#RUN_ARGS[@]}-1]}" == "${RFID_SCRIPT} --reader pn532_i2c_py532 --deps no --force" ]] \
    || fail "RFID_READER_DEPS=no was not forwarded in non-interactive mode"
unset RFID_READER_DEPS

# An empty module aborts
RFID_READER_MODULE=""
if ( _run_setup_rfid_reader ) >/dev/null 2>&1; then
    fail "an empty RFID_READER_MODULE was accepted"
fi

# Interactive mode passes no reader arguments
NON_INTERACTIVE=false
RUN_ARGS=()
_run_setup_rfid_reader
[[ "${RUN_ARGS[${#RUN_ARGS[@]}-1]}" == "${RFID_SCRIPT}" ]] \
    || fail "interactive mode received unexpected reader arguments"

# A non-zero exit of the reader tool aborts the installation (the tool may
# reject e.g. a reader that cannot be configured without a terminal)
NON_INTERACTIVE=true
RFID_READER_MODULE="generic_usb"
run_and_print_lc() { RUN_ARGS+=("$*"); return 42; }
if ( _run_setup_rfid_reader ) >/dev/null 2>&1; then
    fail "a failing RFID reader configuration was accepted"
fi
run_and_print_lc() { RUN_ARGS+=("$*"); }

unset -f sudo run_and_print_lc exit_on_error

# --- install() enforces option consistency in non-interactive mode ---
source "${REPOSITORY_ROOT}/installation/routines/install.sh"

CALLED=()
customize_options() { CALLED+=("customize_options"); }
_configure_webapp_bundle_download() { CALLED+=("bundle_download"); }
show_slow_hardware_message() { :; }
prepare_dependencies() { :; }
set_raspi_config() { :; }
init_git_repo_from_tardir() { :; }
setup_jukebox_core() { :; }
setup_mpd() { :; }
setup_samba() { :; }
setup_jukebox_webapp() { :; }
setup_kiosk_mode() { :; }
setup_rfid_reader() { :; }
optimize_boot_time() { :; }
setup_autohotspot() { :; }
setup_postinstall() { :; }
cleanup() { :; }
run_and_print_lc() { :; }

NON_INTERACTIVE=true
HIFIBERRY_BOARD=""
ENABLE_WEBAPP=false
ENABLE_KIOSK_MODE=true
ENABLE_AUTOHOTSPOT=true
ENABLE_STATIC_IP=true

install
[[ "${ENABLE_KIOSK_MODE}" == "false" ]] || fail "kiosk mode was not disabled without the WebApp"
[[ "${ENABLE_STATIC_IP}" == "false" ]]  || fail "static IP was not disabled with autohotspot"
[[ " ${CALLED[*]} " != *" customize_options "* ]] || fail "customize_options was called in non-interactive mode"

# The WebApp bundle normalization is re-applied when the WebApp is enabled
CALLED=()
ENABLE_WEBAPP=true
install
[[ " ${CALLED[*]} " == *" bundle_download "* ]] || fail "webapp bundle normalization was not applied"

# The interactive path still calls customize_options
CALLED=()
NON_INTERACTIVE=false
install
[[ " ${CALLED[*]} " == *" customize_options "* ]] || fail "customize_options was not called in interactive mode"

echo "Non-interactive config tests passed"
