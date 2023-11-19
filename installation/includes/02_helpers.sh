#!/usr/bin/env bash

# Helpers

# $1->start, $2->end
calc_runtime_and_print() {
  runtime=$(($2-$1))
  ((h=${runtime}/3600))
  ((m=(${runtime}%3600)/60))
  ((s=${runtime}%60))

  echo "Done in ${h}h ${m}m ${s}s."
}

run_with_timer() {
  local time_start=$(date +%s);

  $1; # Executes the function passed as an argument

  calc_runtime_and_print time_start $(date +%s) | tee /dev/fd/3
  echo "--------------------------------------"
}

_download_file_from_google_drive() {
  GD_SHARING_ID=${1}
  TAR_FILENAME=${2}
  wget --load-cookies /tmp/cookies.txt "https://docs.google.com/uc?export=download&confirm=$(wget --save-cookies /tmp/cookies.txt --keep-session-cookies --no-check-certificate 'https://docs.google.com/uc?export=download&id=${GD_SHARING_ID}' -O- | sed -rn 's/.*confirm=([0-9A-Za-z_]+).*/\1\n/p')&id=${GD_SHARING_ID}" -O ${TAR_FILENAME} && rm -rf /tmp/cookies.txt
  echo "Downloaded from Google Drive ID ${GD_SHARING_ID} into ${TAR_FILENAME}"
}

get_onboard_audio() {
  if grep -q -E "^dtparam=([^,]*,)*audio=(on|true|yes|1).*" ${RPI_BOOT_CONFIG_FILE}
  then
    echo 1
  else
    echo 0
  fi
}

check_os_type() {
  # Check if current distro is a 32 bit version
  # Support for 64 bit Distros has not been checked (or precisely: is known not to work)
  # All RaspianOS versions report as machine "armv6l" or "armv7l", if 32 bit (even the ARMv8 cores!)

  local os_type
  os_type=$(uname -m)

  echo -e "\nChecking OS type '$os_type'" | tee /dev/fd/3

  if [[ $os_type == "armv7l" || $os_type == "armv6l" ]]; then
    echo -e "  ... OK!\n" | tee /dev/fd/3
  else
    echo "ERROR: Only 32 bit operating systems supported. Please use a 32bit version of RaspianOS!" | tee /dev/fd/3
    echo "You can fix this problem for 64bit kernels: https://github.com/MiczFlor/RPi-Jukebox-RFID/issues/2041" | tee /dev/fd/3
    exit 1
  fi
}


##### Check helpers

# Check if the file(s) exists
verify_files_exists() {
    local files="$@"
    echo "Verify '${files}' exists"

    for file in $files
    do
        test ! -f ${file} && exit_on_error "ERROR: '${file}' does not exists or is not a file!"
    done
    echo "CHECK"
}

# Check if the dir(s) exists
verify_dirs_exists() {
    local dirs="$@"
    echo "Verify '${dirs}' exists"

    for dir in $dirs
    do
        test ! -d ${dir} && exit_on_error "ERROR: '${dir}' does not exists or is not a dir!"
    done
    echo "CHECK"
}


# Check if the file(s) has/have the expected owner and modifications
verify_files_chmod_chown() {
    local mod_expected=$1
    local user_expected=$2
    local group_expected=$3
    local files="${@:4}"
    echo "Verify '${mod_expected}' '${user_expected}:${group_expected}' is set for '${files}'"

    for file in $files
    do
        test ! -f ${file} && exit_on_error "ERROR: '${file}' does not exists or is not a file!"

        mod_actual=$(stat --format '%a' "${file}")
        user_actual=$(stat -c '%U' "${file}")
        group_actual=$(stat -c '%G' "${file}")
        test ! "${mod_expected}" -eq "${mod_actual}" && exit_on_error "ERROR: '${file}' actual mod '${mod_actual}' differs from expected '${mod_expected}'!"
        test ! "${user_expected}" == "${user_actual}" && exit_on_error "ERROR: '${file}' actual owner '${user_actual}' differs from expected '${user_expected}'!"
        test ! "${group_expected}" == "${group_actual}" && exit_on_error "ERROR: '${file}' actual group '${group_actual}' differs from expected '${group_expected}'!"
    done
    echo "CHECK"
}

# Check if the dir(s) has/have the expected owner and modifications
verify_dirs_chmod_chown() {
    local mod_expected=$1
    local user_expected=$2
    local group_expected=$3
    local dirs="${@:4}"
    echo "Verify '${mod_expected}' '${user_expected}:${group_expected}' is set for '${dirs}'"

    for dir in $dirs
    do
        test ! -d ${dir} && exit_on_error "ERROR: '${dir}' does not exists or is not a dir!"

        mod_actual=$(stat --format '%a' "${dir}")
        user_actual=$(stat -c '%U' "${dir}")
        group_actual=$(stat -c '%G' "${dir}")
        test ! "${mod_expected}" -eq "${mod_actual}" && exit_on_error "ERROR: '${dir}' actual mod '${mod_actual}' differs from expected '${mod_expected}'!"
        test ! "${user_expected}" == "${user_actual}" && exit_on_error "ERROR: '${dir}' actual owner '${user_actual}' differs from expected '${user_expected}'!"
        test ! "${group_expected}" == "${group_actual}" && exit_on_error "ERROR: '${dir}' actual group '${group_actual}' differs from expected '${group_expected}'!"
    done
    echo "CHECK"
}

verify_file_contains_string() {
    local string="$1"
    local file="$2"
    echo "Verify '${string}' found in '${file}'"

    if [[ ! $(grep -iw "${string}" "${file}") ]]; then
        exit_on_error "ERROR: '${string}' not found in '${file}'"
    fi
    echo "CHECK"
}

verify_file_contains_string_once() {
    local string="$1"
    local file="$2"
    echo "Verify '${string}' found in '${file}'"

    local file_contains_string_count=$(grep -oiw "${string}" "${file}" | wc -l)
    if [ "$file_contains_string_count" -lt 1 ]; then
        exit_on_error "ERROR: '${string}' not found in '${file}'"
    elif [ "$file_contains_string_count" -gt 1 ]; then
        exit_on_error "ERROR: '${string}' found more than once in '${file}'"
    fi
    echo "CHECK"
}

check_service_state() {
    local service="$1"
    local desired_state="$2"
	local option="${3:+$3 }" # optional, dont't quote in next call!
    echo "Verify service '${option}${service}' is '${desired_state}'"

    local actual_state=$(systemctl is-active ${option}${service})
    if [[ ! "${actual_state}" == "${desired_state}" ]]; then
        exit_on_error "ERROR: service '${option}${service}' is not '${desired_state}' (state: '${actual_state}')."
    fi
    echo "CHECK"
}

check_service_enablement() {
    local service="$1"
    local desired_enablement="$2"
    local option="${3:+$3 }" # optional, dont't quote in next call!
    echo "Verify service ${option}${service} is ${desired_enablement}"

    local actual_enablement=$(systemctl is-enabled ${option}${service})
    if [[ ! "${actual_enablement}" == "${desired_enablement}" ]]; then
        exit_on_error "ERROR: service ${option}${service} is not ${desired_enablement} (state: ${actual_enablement})."
    fi
    echo "CHECK"
}

check_optional_service_enablement() {
    local service="$1"
    local desired_enablement="$2"
    local option="${3:+$3 }" # optional, dont't quote in next call!
    echo "Verify service ${option}${service} is ${desired_enablement}"

    local actual_enablement=$(systemctl is-enabled ${option}${service}) 2>/dev/null
    if [[ -z "${actual_enablement}" ]]; then
        echo "INFO: optional service ${option}${service} is not installed."
    elif [[ "${actual_enablement}" == "static" ]]; then
        echo "INFO: optional service ${option}${service} is set static."
    elif [[ ! "${actual_enablement}" == "${desired_enablement}" ]]; then
        exit_on_error "ERROR: service ${option}${service} is not ${desired_enablement} (state: ${actual_enablement})."
    fi
    echo "CHECK"
}

# Reads a textfile and returns all lines as args.
# Does filter out comments, egg-prefixes and version suffixes
# Arguments:
#   1    : textfile to read
get_args_from_file() {
    local package_file="$1"
    sed 's/.*#egg=//g' ${package_file} | sed -E 's/(#|=|>|<).*//g' | xargs echo
}

# Check if all passed packages are installed. Fail on first missing.
verify_apt_packages() {
    local packages="$@"
    echo "Verify packages are installed: '${packages}'"

    if [ -n "${packages}" ]; then
        local apt_list_installed=$(apt -qq list --installed 2>/dev/null)
        for package in ${packages}
        do
            if [[ ! $(echo "${apt_list_installed}" | grep -i "^${package}/.*installed") ]]; then
                exit_on_error "ERROR: ${package} is not installed"
            fi
        done
    fi
    echo "CHECK"
}

# Check if all passed modules are installed. Fail on first missing.
verify_pip_modules() {
    local modules="$@"
    echo "Verify modules are installed: '${modules}'"

    if [ -n "${modules}" ]; then
        local pip_list_installed=$(pip list 2>/dev/null)
        for module in ${modules}
        do
            if [[ ! $(echo "${pip_list_installed}" | grep -i "^${module} ") ]]; then
                exit_on_error "ERROR: ${module} is not installed"
            fi
        done
    fi
    echo "CHECK"
}
