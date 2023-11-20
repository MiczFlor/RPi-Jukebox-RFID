#!/usr/bin/env bash

### Helpers

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

  calc_runtime_and_print time_start $(date +%s) | tee /dev/fd/3
}

run_with_log_frame() {
    local time_start=$(date +%s);
    local description="$2"
    echo -e "\n\n"
    echo "#########################################################"
    echo "${description}" | tee /dev/fd/3

    $1; # Executes the function passed as an argument

    local done_in=$(calc_runtime_and_print time_start $(date +%s))
    echo -e "\n${done_in} - ${description}"
    echo "#########################################################"
}

_download_file_from_google_drive() {
  GD_SHARING_ID=${1}
  TAR_FILENAME=${2}
  wget --load-cookies /tmp/cookies.txt "https://docs.google.com/uc?export=download&confirm=$(wget --save-cookies /tmp/cookies.txt --keep-session-cookies --no-check-certificate 'https://docs.google.com/uc?export=download&id=${GD_SHARING_ID}' -O- | sed -rn 's/.*confirm=([0-9A-Za-z_]+).*/\1\n/p')&id=${GD_SHARING_ID}" -O ${TAR_FILENAME} && rm -rf /tmp/cookies.txt
  echo "Downloaded from Google Drive ID ${GD_SHARING_ID} into ${TAR_FILENAME}"
}


### Verify helpers

print_verify_installation() {
    echo ""
    echo "  -------------------------------------------------------"
    echo "  Check installation"
    echo ""
}

# Check if the file(s) exists
verify_files_exists() {
    local files="$@"
    echo "  Verify '${files}' exists"

    if [[ -z "${files}" ]]; then
        exit_on_error "ERROR: at least one parameter value is missing!"
    fi

    for file in $files
    do
        test ! -f ${file} && exit_on_error "ERROR: '${file}' does not exists or is not a file!"
    done
    echo "  CHECK"
}

# Check if the dir(s) exists
verify_dirs_exists() {
    local dirs="$@"
    echo "  Verify '${dirs}' exists"

    if [[ -z "${dirs}" ]]; then
        exit_on_error "ERROR: at least one parameter value is missing!"
    fi

    for dir in $dirs
    do
        test ! -d ${dir} && exit_on_error "ERROR: '${dir}' does not exists or is not a dir!"
    done
    echo "  CHECK"
}

# Check if the file(s) has/have the expected owner and modifications
verify_files_chmod_chown() {
    local mod_expected=$1
    local user_expected=$2
    local group_expected=$3
    local files="${@:4}"
    echo "  Verify '${mod_expected}' '${user_expected}:${group_expected}' is set for '${files}'"

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
    echo "  CHECK"
}

# Check if the dir(s) has/have the expected owner and modifications
verify_dirs_chmod_chown() {
    local mod_expected=$1
    local user_expected=$2
    local group_expected=$3
    local dirs="${@:4}"
    echo "  Verify '${mod_expected}' '${user_expected}:${group_expected}' is set for '${dirs}'"

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
    echo "  CHECK"
}

verify_file_contains_string() {
    local string="$1"
    local file="$2"
    echo "  Verify '${string}' found in '${file}'"

    if [[ -z "${string}" || -z "${file}" ]]; then
        exit_on_error "ERROR: at least one parameter value is missing!"
    fi

    if [[ ! $(grep -iw "${string}" "${file}") ]]; then
        exit_on_error "ERROR: '${string}' not found in '${file}'"
    fi
    echo "  CHECK"
}

verify_file_contains_string_once() {
    local string="$1"
    local file="$2"
    echo "  Verify '${string}' found in '${file}'"

    if [[ -z "${string}" || -z "${file}" ]]; then
        exit_on_error "ERROR: at least one parameter value is missing!"
    fi

    local file_contains_string_count=$(grep -oiw "${string}" "${file}" | wc -l)
    if [ "$file_contains_string_count" -lt 1 ]; then
        exit_on_error "ERROR: '${string}' not found in '${file}'"
    elif [ "$file_contains_string_count" -gt 1 ]; then
        exit_on_error "ERROR: '${string}' found more than once in '${file}'"
    fi
    echo "  CHECK"
}

verify_service_state() {
    local service="$1"
    local desired_state="$2"
	local option="${3:+$3 }" # optional, dont't quote in next call!
    echo "  Verify service '${option}${service}' is '${desired_state}'"

    if [[ -z "${service}" || -z "${desired_state}" ]]; then
        exit_on_error "ERROR: at least one parameter value is missing!"
    fi

    local actual_state=$(systemctl is-active ${option}${service})
    if [[ ! "${actual_state}" == "${desired_state}" ]]; then
        exit_on_error "ERROR: service '${option}${service}' is not '${desired_state}' (state: '${actual_state}')."
    fi
    echo "  CHECK"
}

verify_service_enablement() {
    local service="$1"
    local desired_enablement="$2"
    local option="${3:+$3 }" # optional, dont't quote in next call!
    echo "  Verify service ${option}${service} is ${desired_enablement}"

    if [[ -z "${service}" || -z "${desired_enablement}" ]]; then
        exit_on_error "ERROR: at least one parameter value is missing!"
    fi

    local actual_enablement=$(systemctl is-enabled ${option}${service})
    if [[ ! "${actual_enablement}" == "${desired_enablement}" ]]; then
        exit_on_error "ERROR: service ${option}${service} is not ${desired_enablement} (state: ${actual_enablement})."
    fi
    echo "  CHECK"
}

verify_optional_service_enablement() {
    local service="$1"
    local desired_enablement="$2"
    local option="${3:+$3 }" # optional, dont't quote in next call!
    echo "  Verify service ${option}${service} is ${desired_enablement}"

    if [[ -z "${service}" || -z "${desired_enablement}" ]]; then
        exit_on_error "ERROR: at least one parameter value is missing!"
    fi

    local actual_enablement=$(systemctl is-enabled ${option}${service}) 2>/dev/null
    if [[ -z "${actual_enablement}" ]]; then
        echo "  INFO: optional service ${option}${service} is not installed."
    elif [[ "${actual_enablement}" == "static" ]]; then
        echo "  INFO: optional service ${option}${service} is set static."
    elif [[ ! "${actual_enablement}" == "${desired_enablement}" ]]; then
        exit_on_error "ERROR: service ${option}${service} is not ${desired_enablement} (state: ${actual_enablement})."
    fi
    echo "  CHECK"
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
    echo "  Verify packages are installed: '${packages}'"

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
    echo "  CHECK"
}

# Check if all passed modules are installed. Fail on first missing.
verify_pip_modules() {
    local modules="$@"
    echo "  Verify modules are installed: '${modules}'"

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
    echo "  CHECK"
}
