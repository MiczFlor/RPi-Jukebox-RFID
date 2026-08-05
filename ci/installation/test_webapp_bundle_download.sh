#!/usr/bin/env bash

set -euo pipefail

SOURCE="${BASH_SOURCE[0]}"
SCRIPT_DIR="$(dirname "$SOURCE")"
REPOSITORY_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"

source "${REPOSITORY_ROOT}/installation/routines/setup_jukebox_webapp.sh"

TEST_ROOT=$(mktemp -d)
trap 'rm -rf "${TEST_ROOT}"' EXIT

INSTALLATION_PATH="${TEST_ROOT}/RPi-Jukebox-RFID"
GIT_REPO_NAME="RPi-Jukebox-RFID"
GIT_UPSTREAM_USER="MiczFlor"
GIT_USER="contributor"
TEST_COMMIT="0123456789abcdef0123456789abcdef01234567"
TEST_VERSION="3.7.0-alpha"
ATTEMPTED_URLS=()
AVAILABLE_URL=""

mkdir -p "${INSTALLATION_PATH}/src/webapp"
mkdir -p "${TEST_ROOT}/payload/build"
echo "test bundle" > "${TEST_ROOT}/payload/build/index.html"
tar -czf "${TEST_ROOT}/fixture.tar.gz" -C "${TEST_ROOT}/payload" build

print_lc() {
    :
}

print_c() {
    :
}

clear_c() {
    :
}

log() {
    :
}

python() {
    echo "${TEST_VERSION}"
}

git() {
    echo "${TEST_COMMIT}"
}

validate_url() {
    ATTEMPTED_URLS+=("$1")
    [[ "$1" == "${AVAILABLE_URL}" ]]
}

download_from_url() {
    cp "${TEST_ROOT}/fixture.tar.gz" "$2"
}

exit_on_error() {
    echo "$*" >&2
    exit 1
}

reset_download() {
    ATTEMPTED_URLS=()
    AVAILABLE_URL="$1"
    rm -rf "${INSTALLATION_PATH}/src/webapp/build"
}

assert_attempts() {
    local expected=("$@")
    local index

    [[ "${#ATTEMPTED_URLS[@]}" -eq "${#expected[@]}" ]]
    for index in "${!expected[@]}"; do
        [[ "${ATTEMPTED_URLS[$index]}" == "${expected[$index]}" ]]
    done
}

BUNDLE_NAME="webapp-build-${TEST_COMMIT:0:10}.tar.gz"
SOURCE_DEVELOPMENT_URL="https://github.com/${GIT_USER}/${GIT_REPO_NAME}/releases/download/${WEBAPP_DEVELOPMENT_RELEASE_TAG}/${BUNDLE_NAME}"
SOURCE_RELEASE_URL="https://github.com/${GIT_USER}/${GIT_REPO_NAME}/releases/download/v${TEST_VERSION}/${BUNDLE_NAME}"
UPSTREAM_DEVELOPMENT_URL="https://github.com/${GIT_UPSTREAM_USER}/${GIT_REPO_NAME}/releases/download/${WEBAPP_DEVELOPMENT_RELEASE_TAG}/${BUNDLE_NAME}"
UPSTREAM_RELEASE_URL="https://github.com/${GIT_UPSTREAM_USER}/${GIT_REPO_NAME}/releases/download/v${TEST_VERSION}/${BUNDLE_NAME}"
MISMATCHED_URL="https://github.com/${GIT_UPSTREAM_USER}/${GIT_REPO_NAME}/releases/download/${WEBAPP_DEVELOPMENT_RELEASE_TAG}/webapp-build-deadbeef00.tar.gz"

# Prefer the source repository's exact development bundle.
ENABLE_WEBAPP_PROD_DOWNLOAD=true
reset_download "${SOURCE_DEVELOPMENT_URL}"
_jukebox_webapp_download
assert_attempts "${SOURCE_DEVELOPMENT_URL}"
[[ -f "${INSTALLATION_PATH}/src/webapp/build/index.html" ]]

# Fall back only to other exact-commit locations.
reset_download "${UPSTREAM_DEVELOPMENT_URL}"
_jukebox_webapp_download
assert_attempts \
    "${SOURCE_DEVELOPMENT_URL}" \
    "${SOURCE_RELEASE_URL}" \
    "${UPSTREAM_DEVELOPMENT_URL}"

# Release-only mode skips development bundles.
GIT_USER="MiczFlor"
SOURCE_RELEASE_URL="https://github.com/${GIT_USER}/${GIT_REPO_NAME}/releases/download/v${TEST_VERSION}/${BUNDLE_NAME}"
ENABLE_WEBAPP_PROD_DOWNLOAD=release-only
reset_download "${SOURCE_RELEASE_URL}"
_jukebox_webapp_download
assert_attempts "${SOURCE_RELEASE_URL}"

# A differently addressed bundle must not be attempted or installed.
GIT_USER="contributor"
SOURCE_RELEASE_URL="https://github.com/${GIT_USER}/${GIT_REPO_NAME}/releases/download/v${TEST_VERSION}/${BUNDLE_NAME}"
ENABLE_WEBAPP_PROD_DOWNLOAD=true
reset_download "${MISMATCHED_URL}"
if _jukebox_webapp_download; then
    echo "A mismatched Web App bundle was accepted" >&2
    exit 1
fi
assert_attempts \
    "${SOURCE_DEVELOPMENT_URL}" \
    "${SOURCE_RELEASE_URL}" \
    "${UPSTREAM_DEVELOPMENT_URL}" \
    "${UPSTREAM_RELEASE_URL}"
[[ ! -e "${INSTALLATION_PATH}/src/webapp/build" ]]

_jukebox_webapp_register_as_system_service_with_nginx() {
    :
}

_jukebox_webapp_check() {
    :
}

# Missing bundles report the full commit and an actionable CI instruction.
if missing_output=$(_run_setup_jukebox_webapp 2>&1); then
    echo "Installation succeeded without an exact Web App bundle" >&2
    exit 1
fi
[[ "${missing_output}" == *"${TEST_COMMIT}"* ]]
[[ "${missing_output}" == *"Test Build Web App v3"* ]]
[[ "${missing_output}" == *"https://github.com/${GIT_USER}/${GIT_REPO_NAME}/actions/workflows/test_build_webapp_v3.yml"* ]]
[[ "${missing_output}" == *"Actions read/write permissions"* ]]

# The legacy local-build mode fails explicitly.
ENABLE_WEBAPP_PROD_DOWNLOAD=false
if local_output=$(_run_setup_jukebox_webapp 2>&1); then
    echo "Legacy local Web App build mode succeeded" >&2
    exit 1
fi
[[ "${local_output}" == *"Local Web App builds were removed"* ]]
[[ "${local_output}" == *"ENABLE_WEBAPP_PROD_DOWNLOAD=false is unsupported"* ]]

source "${REPOSITORY_ROOT}/installation/routines/customize_options.sh"

GIT_BRANCH="feature/test-bundles"
GIT_BRANCH_RELEASE="future3/main"
GIT_BRANCH_DEVELOP="future3/develop"
GIT_USER="contributor"
GIT_UPSTREAM_USER="MiczFlor"
CI_RUNNING=false

ENABLE_WEBAPP_PROD_DOWNLOAD=release-only
_configure_webapp_bundle_download
[[ "${ENABLE_WEBAPP_PROD_DOWNLOAD}" == true ]]

ENABLE_WEBAPP_PROD_DOWNLOAD=false
_configure_webapp_bundle_download
[[ "${ENABLE_WEBAPP_PROD_DOWNLOAD}" == false ]]

GIT_BRANCH="${GIT_BRANCH_DEVELOP}"
GIT_USER="${GIT_UPSTREAM_USER}"
ENABLE_WEBAPP_PROD_DOWNLOAD=release-only
_configure_webapp_bundle_download
[[ "${ENABLE_WEBAPP_PROD_DOWNLOAD}" == "release-only" ]]

source "${REPOSITORY_ROOT}/installation/routines/prepare_dependencies.sh"

# Bash 3.2 treats an empty array expansion as unset under nounset.
set +u

get_args_from_file() {
    echo "tar"
}

SETUP_MPD=false
ENABLE_SAMBA=false
ENABLE_WEBAPP=true
ENABLE_KIOSK_MODE=false
ENABLE_AUTOHOTSPOT=false

for ENABLE_WEBAPP_PROD_DOWNLOAD in true false release-only; do
    _collect_apt_packages
    [[ " ${APT_PACKAGES[*]} " != *" nodejs "* ]]
    [[ " ${APT_PACKAGES[*]} " != *" npm "* ]]
done

echo "Web App bundle download tests passed"
