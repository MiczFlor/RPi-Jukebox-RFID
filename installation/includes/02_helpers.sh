#!/usr/bin/env bash

### Helpers

show_slow_hardware_message() {
    if [[ $(uname -m) == "armv6l" ]]; then
        print_c "--------------------------------------------------------------------
| Your hardware is a little slower so this will take a while.      |
| Go watch a movie but don't let your computer go to sleep for the |
| SSH connection to remain intact.                                 |
--------------------------------------------------------------------
"
    fi
}

# Get key by item number of associated array
get_key_by_item_number() {
    local -n array="$1"
    local item_number="$2"
    local count=0

    for key in "${!array[@]}"; do
        ((count++))
        if [ "$count" -eq "$item_number" ]; then
            echo "$key"
            return
        fi
    done
}

# $1->start, $2->end
calc_runtime_and_print() {
  runtime=$(($2-$1))
  ((h=${runtime}/3600))
  ((m=(${runtime}%3600)/60))
  ((s=${runtime}%60))

  echo "Done in ${h}h ${m}m ${s}s"
}

run_with_timer() {
  local time_start=$(date +%s);

  $1; # Executes the function passed as an argument

  run_and_print_lc calc_runtime_and_print time_start $(date +%s)
}

run_with_log_frame() {
    local time_start=$(date +%s);
    local description="$2"
    log "\n\n"
    log "#########################################################"
    print_lc "${description}"

    $1; # Executes the function passed as an argument

    local done_in=$(calc_runtime_and_print time_start $(date +%s))
    log "\n${done_in} - ${description}"
    log "#########################################################"
}

get_architecture() {
    local arch=""
    if [ "$(uname -m)" = "armv7l" ]; then
        arch="armv7"
    elif [ "$(uname -m)" = "armv6l" ]; then
        arch="armv6"
    elif [ "$(uname -m)" = "aarch64" ]; then
        arch="arm64"
    else
        arch="$(uname -m)"
    fi

    echo $arch
}

is_debian_based() {
    local os_release_id=$( . /etc/os-release; printf '%s\n' "$ID"; )
    if [[ "$os_release_id" == *"raspbian"* ]] || [[ "$os_release_id" == *"debian"* ]]; then
        echo true
    else
        echo false
    fi
}

_get_debian_version_number() {
    if [ "$(is_debian_based)" = true ]; then
        local debian_version_number=$( . /etc/os-release; printf '%s\n' "$VERSION_ID"; )
        echo "$debian_version_number"
    else
        echo "-1"
    fi
}

is_debian_version_at_least() {
    local expected_version=$1
    local debian_version_number=$(_get_debian_version_number)

    if [ "$debian_version_number" -ge "$expected_version" ]; then
        echo true
    else
        echo false
    fi
}

_get_boot_file_path() {
    local filename="$1"
    if [ "$(is_debian_version_at_least 12)" = true ]; then
        echo "/boot/firmware/${filename}"
    else
        echo "/boot/${filename}"
    fi
}

get_boot_config_path() {
    echo $(_get_boot_file_path "config.txt")
}

get_boot_cmdline_path() {
    echo $(_get_boot_file_path "cmdline.txt")
}

validate_url() {
    local url=$1
    wget --spider ${url} >/dev/null 2>&1
    return $?
}

download_from_url() {
    local url=$1
    local output_filename=$2
    wget ${url} -O ${output_filename} || exit_on_error "Download failed"
    return $?
}

get_string_length() {
    local string="$1"
    # "-n" option is needed otherwise an additional linebreak char is added by echo
    echo -n ${string} | wc -m
}

_get_service_enablement() {
    local service="$1"
    local option="${2:+$2 }" # optional, dont't quote in 'systemctl' call!

    if [[ -z "${service}" ]]; then
        exit_on_error "ERROR: at least one parameter value is missing!"
    fi

    local actual_enablement=$(systemctl is-enabled ${option}${service} 2>/dev/null)

    echo "$actual_enablement"
}

is_service_enabled() {
    local service="$1"
    local option="$2"
    local actual_enablement=$(_get_service_enablement $service $option)

    if [[ "$actual_enablement" == "enabled" ]]; then
        echo true
    else
        echo false
    fi
}

is_dhcpcd_enabled() {
    echo $(is_service_enabled "dhcpcd.service")
}

is_NetworkManager_enabled() {
    echo $(is_service_enabled "NetworkManager.service")
}

# create flag file if files does no exist (*.remove) or copy present conf to backup file (*.orig)
# to correctly handling de-/activation of corresponding feature
config_file_backup() {
    local config_file="$1"
    local config_flag_file="${config_file}.remove"
    local config_orig_file="${config_file}.orig"
    if [ ! -f "${config_file}" ]; then
        sudo touch "${config_flag_file}"
    elif [ ! -f "${config_orig_file}" ] && [ ! -f "${config_flag_file}" ]; then
        sudo cp "${config_file}" "${config_orig_file}"
    fi
}

# revert config files backed up with `config_file_backup`
config_file_revert() {
    local config_file="$1"
    local config_flag_file="${config_file}.remove"
    local config_orig_file="${config_file}.orig"
    if [ -f "${config_flag_file}" ]; then
        sudo rm "${config_flag_file}" "${config_file}"
    elif [ -f "${config_orig_file}" ]; then
        sudo mv "${config_orig_file}" "${config_file}"
    fi
}

### Verify helpers
print_verify_installation() {
    log "\n
  -------------------------------------------------------
  Check installation
"
}

# Check if the file(s) exists
verify_files_exists() {
    local files="$@"
    log "  Verify '${files}' exists"

    if [[ -z "${files}" ]]; then
        exit_on_error "ERROR: at least one parameter value is missing!"
    fi

    for file in $files
    do
        test ! -f ${file} && exit_on_error "ERROR: '${file}' does not exists or is not a file!"
    done
    log "  CHECK"
}

# Check if the dir(s) exists
verify_dirs_exists() {
    local dirs="$@"
    log "  Verify '${dirs}' exists"

    if [[ -z "${dirs}" ]]; then
        exit_on_error "ERROR: at least one parameter value is missing!"
    fi

    for dir in $dirs
    do
        test ! -d ${dir} && exit_on_error "ERROR: '${dir}' does not exists or is not a dir!"
    done
    log "  CHECK"
}

# Check if the file(s) has/have the expected owner and modifications
verify_files_chmod_chown() {
    local mod_expected=$1
    local user_expected=$2
    local group_expected=$3
    local files="${@:4}"
    log "  Verify '${mod_expected}' '${user_expected}:${group_expected}' is set for '${files}'"

    if [[ -z "${mod_expected}" || -z "${user_expected}" || -z "${group_expected}" || -z "${files}" ]]; then
        exit_on_error "ERROR: at least one parameter value is missing!"
    fi

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
    log "  CHECK"
}

# Check if the dir(s) has/have the expected owner and modifications
verify_dirs_chmod_chown() {
    local mod_expected=$1
    local user_expected=$2
    local group_expected=$3
    local dirs="${@:4}"
    log "  Verify '${mod_expected}' '${user_expected}:${group_expected}' is set for '${dirs}'"

    if [[ -z "${mod_expected}" || -z "${user_expected}" || -z "${group_expected}" || -z "${dirs}" ]]; then
        exit_on_error "ERROR: at least one parameter value is missing!"
    fi

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
    log "  CHECK"
}

verify_file_contains_string() {
    local string="$1"
    local file="$2"
    log "  Verify '${string}' found in '${file}'"

    if [[ -z "${string}" || -z "${file}" ]]; then
        exit_on_error "ERROR: at least one parameter value is missing!"
    fi

    if [[ ! $(sudo grep -iw "${string}" "${file}") ]]; then
        exit_on_error "ERROR: '${string}' not found in '${file}'"
    fi
    log "  CHECK"
}

verify_file_does_not_contain_string() {
    local string="$1"
    local file="$2"
    log "  Verify '${string}' not found in '${file}'"

    if [[ -z "${string}" || -z "${file}" ]]; then
        exit_on_error "ERROR: at least one parameter value is missing!"
    fi

    if grep -iq "${string}" "${file}"; then
        exit_on_error "ERROR: '${string}' found in '${file}'"
    fi
    log "  CHECK"
}

verify_file_contains_string_once() {
    local string="$1"
    local file="$2"
    log "  Verify '${string}' found in '${file}'"

    if [[ -z "${string}" || -z "${file}" ]]; then
        exit_on_error "ERROR: at least one parameter value is missing!"
    fi

    local file_contains_string_count=$(sudo grep -oiw "${string}" "${file}" | wc -l)
    if [ "$file_contains_string_count" -lt 1 ]; then
        exit_on_error "ERROR: '${string}' not found in '${file}'"
    elif [ "$file_contains_string_count" -gt 1 ]; then
        exit_on_error "ERROR: '${string}' found more than once in '${file}'"
    fi
    log "  CHECK"
}

verify_service_state() {
    local service="$1"
    local desired_state="$2"
    local option="${3:+$3 }" # optional, dont't quote in next call!
    log "  Verify service '${option}${service}' is '${desired_state}'"

    if [[ -z "${service}" || -z "${desired_state}" ]]; then
        exit_on_error "ERROR: at least one parameter value is missing!"
    fi

    local actual_state=$(systemctl is-active ${option}${service})
    if [[ ! "${actual_state}" == "${desired_state}" ]]; then
        exit_on_error "ERROR: service '${option}${service}' is not '${desired_state}' (state: '${actual_state}')."
    fi
    log "  CHECK"
}

verify_service_enablement() {
    local service="$1"
    local desired_enablement="$2"
    local option="$3"
    log "  Verify service ${option}${service} is ${desired_enablement}"

    if [[ -z "${service}" || -z "${desired_enablement}" ]]; then
        exit_on_error "ERROR: at least one parameter value is missing!"
    fi

    local actual_enablement=$(_get_service_enablement $service $option)
    if [[ ! "${actual_enablement}" == "${desired_enablement}" ]]; then
        exit_on_error "ERROR: service ${option}${service} is not ${desired_enablement} (state: ${actual_enablement})."
    fi
    log "  CHECK"
}

verify_optional_service_enablement() {
    local service="$1"
    local desired_enablement="$2"
    local option="$3"
    log "  Verify service ${option}${service} is ${desired_enablement}"

    if [[ -z "${service}" || -z "${desired_enablement}" ]]; then
        exit_on_error "ERROR: at least one parameter value is missing!"
    fi

    local actual_enablement=$(_get_service_enablement $service $option)
    if [[ -z "${actual_enablement}" ]]; then
        log "  INFO: optional service ${option}${service} is not installed."
    elif [[ "${actual_enablement}" == "static" ]]; then
        log "  INFO: optional service ${option}${service} is set static."
    elif [[ ! "${actual_enablement}" == "${desired_enablement}" ]]; then
        exit_on_error "ERROR: service ${option}${service} is not ${desired_enablement} (state: ${actual_enablement})."
    fi
    log "  CHECK"
}

# Reads a textfile and returns all lines as args.
# Does filter out comments, egg-prefixes and version suffixes
# Arguments:
#   1    : textfile to read
get_args_from_file() {
    local package_file="$1"
    sed 's/.*#egg=//g' ${package_file} | sed -E 's/(#|=|>|<|;).*//g' | xargs echo
}

# Check if all passed packages are installed. Fail on first missing.
verify_apt_packages() {
    local packages="$@"
    log "  Verify packages are installed: '${packages}'"

    if [[ -z "${packages}" ]]; then
        exit_on_error "ERROR: at least one parameter value is missing!"
    fi

    local apt_list_installed=$(apt -qq list --installed 2>/dev/null)
    for package in ${packages}
    do
        if [[ ! $(echo "${apt_list_installed}" | grep -i "^${package}/.*installed") ]]; then
            exit_on_error "ERROR: ${package} is not installed"
        fi
    done
    log "  CHECK"
}

# Check if all passed modules are installed. Fail on first missing.
verify_pip_modules() {
    local modules="$@"
    log "  Verify modules are installed: '${modules}'"

    if [[ -z "${modules}" ]]; then
        exit_on_error "ERROR: at least one parameter value is missing!"
    fi

    local pip_list_installed=$(pip list 2>/dev/null)
    for module in ${modules}
    do
        if [[ ! $(echo "${pip_list_installed}" | grep -i "^${module} ") ]]; then
            exit_on_error "ERROR: ${module} is not installed"
        fi
    done
    log "  CHECK"
}

# Check if all passed modules are not installed. Fail on first found.
verify_pip_modules_not() {
    local modules="$@"
    log "  Verify modules are not installed: '${modules}'"

    if [[ -z "${modules}" ]]; then
        exit_on_error "ERROR: at least one parameter value is missing!"
    fi

    local pip_list_installed=$(pip list 2>/dev/null)
    for module in ${modules}
    do
        if [[ $(echo "${pip_list_installed}" | grep -i "^${module} ") ]]; then
            exit_on_error "ERROR: ${module} is installed"
        fi
    done
    log "  CHECK"
}
