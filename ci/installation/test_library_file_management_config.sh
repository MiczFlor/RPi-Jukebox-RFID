#!/usr/bin/env bash

set -euo pipefail

SOURCE="${BASH_SOURCE[0]}"
SCRIPT_DIR="$(dirname "$SOURCE")"
REPOSITORY_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"
NGINX_CONFIG="${REPOSITORY_ROOT}/resources/default-settings/nginx.default"

grep -Fq 'location = /api/v1/library/files' "${NGINX_CONFIG}"

UPLOAD_LOCATION=$(
    sed -n \
        '/location = \/api\/v1\/library\/files {/,/^[[:space:]]*}/p' \
        "${NGINX_CONFIG}"
)
grep -Fq 'client_max_body_size 1g;' <<< "${UPLOAD_LOCATION}"
grep -Fq 'client_body_timeout 1h;' <<< "${UPLOAD_LOCATION}"
grep -Fq 'proxy_request_buffering off;' <<< "${UPLOAD_LOCATION}"
grep -Fq 'proxy_read_timeout 1h;' <<< "${UPLOAD_LOCATION}"
grep -Fq 'proxy_send_timeout 1h;' <<< "${UPLOAD_LOCATION}"

API_LOCATION=$(
    sed -n \
        '/location \/api\/ {/,/^[[:space:]]*}/p' \
        "${NGINX_CONFIG}"
)
grep -Fq 'client_max_body_size 1m;' <<< "${API_LOCATION}"
if grep -Fq 'proxy_request_buffering off;' <<< "${API_LOCATION}"; then
    echo "Request buffering must only be disabled for file uploads" >&2
    exit 1
fi

source "${REPOSITORY_ROOT}/installation/includes/01_default_config.sh"
[[ "${ENABLE_SAMBA}" == false ]]

clear_c() {
    :
}

print_c() {
    :
}

log() {
    :
}

source "${REPOSITORY_ROOT}/installation/routines/customize_options.sh"

ENABLE_SAMBA=true
_option_samba <<< ''
[[ "${ENABLE_SAMBA}" == false ]]

ENABLE_SAMBA=false
_option_samba <<< 'y'
[[ "${ENABLE_SAMBA}" == true ]]

ENABLE_SAMBA=true
_option_samba <<< 'n'
[[ "${ENABLE_SAMBA}" == false ]]

echo "Library file-management configuration tests passed"
