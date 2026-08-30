#!/usr/bin/env bash
# One-line install script for the Jukebox Version 3
#
# To install, simply execute
# cd; bash <(wget -qO- https://raw.githubusercontent.com/MiczFlor/RPi-Jukebox-RFID/future3/develop/installation/install-jukebox.sh)
#
# If you want to get a specific branch or a different repository (mainly for developers)
# you may specify them like this
# cd; GIT_USER='MiczFlor' GIT_BRANCH='future3/develop' bash <(wget -qO- https://raw.githubusercontent.com/MiczFlor/RPi-Jukebox-RFID/future3/develop/installation/install-jukebox.sh)
#
export LC_ALL=C

# Set Repo variables if not specified when calling the script
GIT_USER=${GIT_USER:-"MiczFlor"}
GIT_BRANCH=${GIT_BRANCH:-"future3/main"}

# === Non-interactive installation support ===
# In non-interactive mode all options are supplied via a flat KEY=VALUE
# config file (install_config.env) which is passed as:
#   bash install-jukebox.sh --config /tmp/install_config.env
# This skips all interactive 'read' prompts and installs with the supplied options.
# Values already provided through the environment (the documented env-var-only
# variant: NON_INTERACTIVE=true ...) are honoured; command-line options below
# take precedence.
INSTALL_CONFIG_FILE="${INSTALL_CONFIG_FILE:-}"
NON_INTERACTIVE="${NON_INTERACTIVE:-false}"

while [[ $# -gt 0 ]]; do
    case "$1" in
        --config)
            INSTALL_CONFIG_FILE="$2"
            NON_INTERACTIVE=true
            shift 2
            ;;
        --non-interactive)
            NON_INTERACTIVE=true
            shift
            ;;
        *)
            echo "Unknown option: $1"
            echo "Usage: $0 [--config <file>] [--non-interactive]"
            exit 1
            ;;
    esac
done

# Constants
GIT_REPO_NAME="RPi-Jukebox-RFID"
GIT_URL="https://github.com/${GIT_USER}/${GIT_REPO_NAME}"

CURRENT_USER="${SUDO_USER:-$(whoami)}"
CURRENT_USER_GROUP=$(id -gn "$CURRENT_USER")
HOME_PATH=$(getent passwd "$CURRENT_USER" | cut -d: -f6)

INSTALLATION_PATH="${HOME_PATH}/${GIT_REPO_NAME}"
INSTALL_ID=$(date +%s)
INSTALLATION_LOGFILE="${HOME_PATH}/INSTALL-${INSTALL_ID}.log"

# Manipulate file descriptor for logging
_setup_logging(){
    if [ "$CI_RUNNING" == "true" ]; then
        exec 3>&1 2>&1
    else
        exec 3>&1 1>>"${INSTALLATION_LOGFILE}" 2>&1 || { echo "ERROR: Cannot create log file."; exit 1; }
    fi
    echo "Log start: ${INSTALL_ID}"
    # Publish the log file path to the console so a headless (non-interactive)
    # process can tail it for a detailed live log.
    print_lc "INSTALLATION_LOGFILE=${INSTALLATION_LOGFILE}"
}

# Function to log to both console and logfile
print_lc() {
  local message="$1"
  echo -e "$message" | tee /dev/fd/3
}

# Function to log to logfile only
log() {
  local message="$1"
  echo -e "$message"
}

# Function to run a command where the output will be logged to both console and logfile
# Note: propagate the command's exit code via PIPESTATUS — a plain pipe to
# 'tee' would return tee's exit status (0) and silently hide failures.
run_and_print_lc() {
  "$@" | tee /dev/fd/3
  return "${PIPESTATUS[0]}"
}

# Function to log to console only
print_c() {
  local message="$1"
  echo -e "$message" 1>&3
}

# Function to clear console screen
clear_c() {
  clear 1>&3
}

# Generic emergency error handler that exits the script immediately
# Print additional custom message if passed as first argument
# Examples:
#   a command || exit_on_error
#   a command || exit_on_error "Execution of command failed"
exit_on_error () {
  print_lc "\n****************************************"
  print_lc "ERROR OCCURRED!
A non-recoverable error occurred.
Check install log for details:"
  print_lc "$INSTALLATION_LOGFILE"
  print_lc "****************************************"
  if [[ -n $1 ]]; then
    print_lc "$1"
    print_lc "****************************************"
  fi
  log "Abort!"
  exit 1
}

# Load a non-interactive install configuration file (flat KEY=VALUE).
# Must run after _setup_logging (needs print_lc/log) and before
# _check_existing_installation (which consumes EXISTING_INSTALL_ACTION).
_load_install_config() {
    if [[ -n "$INSTALL_CONFIG_FILE" ]]; then
        if [[ ! -f "$INSTALL_CONFIG_FILE" ]]; then
            print_lc "ERROR: Config file not found: $INSTALL_CONFIG_FILE"
            exit 1
        fi
        print_lc "Loading install configuration from: $INSTALL_CONFIG_FILE"

        # The config file is a flat KEY=VALUE file (install_config.env); no YAML
        # parser is needed on the Pi — the values are simply sourced.
        # shellcheck disable=SC1090
        source "$INSTALL_CONFIG_FILE"
        NON_INTERACTIVE=true

        # GIT_USER/GIT_BRANCH may have been overridden by the config. GIT_URL
        # was computed above (before sourcing) and must be recomputed for forks.
        GIT_URL="https://github.com/${GIT_USER}/${GIT_REPO_NAME}"

        log "Configuration loaded from: $INSTALL_CONFIG_FILE"
    fi
}

_check_existing_installation() {
    if [[ -e "${INSTALLATION_PATH}" ]]; then
        # Backward-compatible: the interactive flow keeps the hard abort.
        if [[ "${NON_INTERACTIVE:-}" != "true" ]]; then
            print_lc "
############## EXISTING INSTALLATION FOUND ##############
Rerunning the installation over an existing installation is
currently not supported (overwrites settings, etc).
Please backup your 'shared' folder and manually changed
files and run the installation on a fresh image."
            exit 1
        fi

        print_lc "
############## EXISTING INSTALLATION FOUND ##############
An existing installation was found at ${INSTALLATION_PATH}."

        case "${EXISTING_INSTALL_ACTION:-backup}" in
            remove)
                print_lc "Removing existing installation (user chose 'Remove')."
                rm -rf "${INSTALLATION_PATH}"
                ;;
            backup)
                local ts backup_dir
                ts=$(date +%Y%m%d-%H%M%S)
                backup_dir="${INSTALLATION_PATH}.bak-${ts}"
                print_lc "Backing up existing installation to ${backup_dir} (user chose 'Backup')."
                mv "${INSTALLATION_PATH}" "${backup_dir}"
                ;;
            *)
                print_lc "Unknown EXISTING_INSTALL_ACTION '${EXISTING_INSTALL_ACTION}'. Aborting."
                exit 1
                ;;
        esac
    fi
}

# Fail fast on an invalid non-interactive configuration instead of
# discovering the problem halfway through the installation (after the
# dependencies have already been installed).
_validate_noninteractive_config() {
    if [[ "${NON_INTERACTIVE:-}" != "true" ]]; then
        return 0
    fi
    # ENABLE_RFID_READER defaults to true (see 01_default_config.sh); at this
    # point the defaults are not sourced yet, so treat an unset variable as true.
    local enable_rfid_reader="${ENABLE_RFID_READER:-true}"
    if [[ "$enable_rfid_reader" == true && -z "${RFID_READER_MODULE:-}" ]]; then
        print_lc "ERROR: RFID reader is enabled (ENABLE_RFID_READER defaults to true) but no reader module was configured."
        print_lc "In non-interactive mode set RFID_READER_MODULE in your config file,"
        print_lc "or disable the reader setup with ENABLE_RFID_READER=false."
        exit 1
    fi
    # The dependency-handling mode must not prompt in non-interactive mode,
    # so 'query' is not allowed (it would block on a read prompt).
    if [[ -n "${RFID_READER_DEPS:-}" && "${RFID_READER_DEPS}" != "auto" && "${RFID_READER_DEPS}" != "no" ]]; then
        print_lc "ERROR: RFID_READER_DEPS must be 'auto' or 'no' in non-interactive mode (got '${RFID_READER_DEPS}')."
        print_lc "'query' would prompt for confirmation and is therefore not allowed."
        exit 1
    fi
}

_download_jukebox_source() {
  log "#########################################################"
  print_c "Downloading Phoniebox software from Github ..."
  print_lc "Download Source: ${GIT_URL}/${GIT_BRANCH}"

  cd "${HOME_PATH}" || exit_on_error "ERROR: Changing to home dir failed."
  wget -qO- "${GIT_URL}/tarball/${GIT_BRANCH}" | tar xz
  # Use case insensitive search/sed because user names in Git Hub are case insensitive
  local git_repo_download=$(find . -maxdepth 1 -type d -iname "${GIT_USER}-${GIT_REPO_NAME}-*")
  log "GIT REPO DOWNLOAD = $git_repo_download"
  GIT_HASH=$(echo "$git_repo_download" | sed -rn "s/.*${GIT_USER}-${GIT_REPO_NAME}-([0-9a-fA-F]+)/\1/ip")
  # Save the git hash for this particular download for later git repo initialization
  log "GIT HASH = $GIT_HASH"
  if [[ -z "${git_repo_download}" ]]; then
    exit_on_error "ERROR: Couldn't find git download."
  fi
  if [[ -z "${GIT_HASH}" ]]; then
    exit_on_error "ERROR: Couldn't determine git hash from download."
  fi
  mv "$git_repo_download" "$GIT_REPO_NAME" || exit_on_error "ERROR: Can't overwrite existing installation."
  log "\nDONE: Downloading Phoniebox software from Github"
  log "#########################################################"
}

_load_sources() {
    # Load / Source dependencies
    for i in "${INSTALLATION_PATH}"/installation/includes/*; do
        source "$i" || exit_on_error
    done

    for j in "${INSTALLATION_PATH}"/installation/routines/*; do
        source "$j" || exit_on_error
    done
}

### SETUP LOGGING
_setup_logging

### LOAD NON-INTERACTIVE CONFIG (if any)
_load_install_config

# Echo the effective repo (after any --config override) for log clarity.
echo GIT_BRANCH $GIT_BRANCH
echo GIT_URL $GIT_URL

### VALIDATE NON-INTERACTIVE CONFIG
_validate_noninteractive_config

### CHECK PREREQUISITE
_check_existing_installation

### RUN INSTALLATION
log "Current User: $CURRENT_USER"
log "User home dir: $HOME_PATH"

_download_jukebox_source
cd "${INSTALLATION_PATH}" || exit_on_error "ERROR: Changing to install dir failed."
_load_sources

welcome
run_with_timer install
finish
