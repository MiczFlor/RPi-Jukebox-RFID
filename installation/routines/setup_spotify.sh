#!/usr/bin/env bash

LIBRESPOT_VERSION="0.8.0"
LIBRESPOT_REVISION="303026bba2af4c31e710afefc3aad4a89e38c812"
LIBRESPOT_BUILD_ID="303026bb-phoniebox1"
LIBRESPOT_RELEASE_TAG="librespot-builds"
LIBRESPOT_REPOSITORY="https://github.com/librespot-org/librespot.git"
LIBRESPOT_BUILD_DEPENDENCIES=(cargo libpulse-dev libssl-dev pkg-config)
LIBRESPOT_BUILD_DEPENDENCIES_TO_REMOVE=()
LIBRESPOT_CHECKSUMS_FILE="${LIBRESPOT_CHECKSUMS_FILE:-${INSTALLATION_PATH}/installation/librespot-checksums.sha256}"
LIBRESPOT_SERVICE_PATH="${SYSTEMD_USR_PATH}/librespot.service"
JUKEBOX_SPOTIFY_DROPIN_DIR="${SYSTEMD_USR_PATH}/jukebox-daemon.service.d"
JUKEBOX_SPOTIFY_DROPIN="${JUKEBOX_SPOTIFY_DROPIN_DIR}/spotify.conf"

_spotify_validate_configuration() {
  if [[ -z "${SPOTIFY_CLIENT_ID}" || -z "${SPOTIFY_REDIRECT_URI}" ]]; then
    exit_on_error "Spotify requires a client ID and OAuth redirect URI."
  fi
  if [[ ! "${SPOTIFY_DEVICE_NAME}" =~ ^[A-Za-z0-9._\ -]+$ ]]; then
    exit_on_error "Spotify device names may only contain letters, numbers, spaces, '.', '_', and '-'."
  fi
}

_spotify_enable_ipv6() {
  local cmdline_file
  local updated_cmdline
  cmdline_file=$(get_boot_cmdline_path)
  [[ -f "${cmdline_file}" ]] || return

  if grep -Eq '(^|[[:space:]])ipv6\.disable=1([[:space:]]|$)' "${cmdline_file}"; then
    print_lc "  Re-enable IPv6 for librespot discovery"
    updated_cmdline=$(sed -E \
      -e 's/(^|[[:space:]])ipv6\.disable=1([[:space:]]|$)/ /g' \
      -e 's/[[:space:]]+/ /g' \
      -e 's/^ //; s/ $//' \
      "${cmdline_file}") \
      || exit_on_error "Failed to remove ipv6.disable=1 from ${cmdline_file}."
    printf '%s\n' "${updated_cmdline}" | sudo tee "${cmdline_file}" >/dev/null \
      || exit_on_error "Failed to update ${cmdline_file}."
  fi
}

_spotify_librespot_architecture() {
  case "${1:-$(uname -m)}" in
    armv7l|armv7)
      printf '%s\n' armv7
      ;;
    aarch64|arm64)
      printf '%s\n' arm64
      ;;
    x86_64|amd64)
      printf '%s\n' amd64
      ;;
    armv6l|armv6)
      printf '%s\n' armv6
      ;;
    *)
      return 1
      ;;
  esac
}

_spotify_archive_name() {
  printf 'librespot-%s-linux-%s.tar.gz\n' "${LIBRESPOT_BUILD_ID}" "$1"
}

_spotify_expected_checksum() {
  local archive_name="$1"
  [[ -r "${LIBRESPOT_CHECKSUMS_FILE}" ]] || return 1
  awk -v archive_name="${archive_name}" \
    '$2 == archive_name { print $1; found = 1; exit }
     END { if (!found) exit 1 }' \
    "${LIBRESPOT_CHECKSUMS_FILE}"
}

_spotify_verify_archive() {
  local archive_path="$1"
  local archive_name="$2"
  local expected_checksum
  local actual_checksum

  expected_checksum=$(_spotify_expected_checksum "${archive_name}") || return 1
  actual_checksum=$(sha256sum "${archive_path}" | awk '{ print $1 }') \
    || return 1
  [[ "${actual_checksum}" == "${expected_checksum}" ]]
}

_spotify_try_download() {
  local download_url="$1"
  local archive_path="$2"
  local archive_name="$3"

  print_lc "    Checking ${download_url}"
  if ! validate_url "${download_url}"; then
    log "    Librespot archive not found: ${download_url}"
    return 1
  fi

  print_lc "    Downloading ${download_url}"
  if ! wget --timeout=30 --tries=3 "${download_url}" -O "${archive_path}"; then
    rm -f "${archive_path}"
    log "    Failed to download librespot archive: ${download_url}"
    return 1
  fi
  if ! _spotify_verify_archive "${archive_path}" "${archive_name}"; then
    rm -f "${archive_path}"
    print_lc "    Warning: rejected librespot archive with an invalid checksum."
    return 1
  fi
}

_spotify_download_archive() {
  local archive_path="$1"
  local archive_name="$2"
  local source_url
  local upstream_url
  local git_user_normalized
  local git_upstream_user_normalized

  source_url="https://github.com/${GIT_USER}/${GIT_REPO_NAME}/releases/download/${LIBRESPOT_RELEASE_TAG}/${archive_name}"
  upstream_url="https://github.com/${GIT_UPSTREAM_USER}/${GIT_REPO_NAME}/releases/download/${LIBRESPOT_RELEASE_TAG}/${archive_name}"
  git_user_normalized=$(printf '%s' "${GIT_USER}" | tr '[:upper:]' '[:lower:]')
  git_upstream_user_normalized=$(printf '%s' "${GIT_UPSTREAM_USER}" | tr '[:upper:]' '[:lower:]')

  if _spotify_try_download "${source_url}" "${archive_path}" "${archive_name}"; then
    return
  fi
  if [[ "${git_user_normalized}" != "${git_upstream_user_normalized}" ]] \
      && _spotify_try_download \
        "${upstream_url}" "${archive_path}" "${archive_name}"; then
    return
  fi
  return 1
}

_spotify_install_prebuilt_librespot() {
  local architecture
  local archive_name
  local install_tmp_dir
  local archive_path
  local extract_dir

  architecture=$(_spotify_librespot_architecture) || return 1
  [[ "${architecture}" != "armv6" ]] || return 1
  archive_name=$(_spotify_archive_name "${architecture}")

  mkdir -p "${HOME_PATH}/.cache" || return 1
  install_tmp_dir=$(mktemp -d "${HOME_PATH}/.cache/librespot-install.XXXXXX") \
    || return 1
  archive_path="${install_tmp_dir}/${archive_name}"
  extract_dir="${install_tmp_dir}/extract"

  if ! _spotify_download_archive "${archive_path}" "${archive_name}"; then
    rm -rf "${install_tmp_dir}"
    return 1
  fi

  if ! mkdir -p "${extract_dir}" "${HOME_PATH}/.local/bin"; then
    rm -rf "${install_tmp_dir}"
    return 1
  fi
  if ! tar -xzf "${archive_path}" -C "${extract_dir}" \
      || [[ ! -f "${extract_dir}/librespot" ]] \
      || ! command install -m 755 \
        "${extract_dir}/librespot" "${HOME_PATH}/.local/bin/librespot"; then
    rm -rf "${install_tmp_dir}"
    return 1
  fi

  rm -rf "${install_tmp_dir}"
}

_spotify_install_build_dependencies() {
  print_lc "  Install librespot build dependencies"

  LIBRESPOT_BUILD_DEPENDENCIES_TO_REMOVE=()
  local package
  for package in "${LIBRESPOT_BUILD_DEPENDENCIES[@]}"; do
    if ! dpkg-query -W -f='${Status}' "${package}" 2>/dev/null \
        | grep -qx "install ok installed"; then
      LIBRESPOT_BUILD_DEPENDENCIES_TO_REMOVE+=("${package}")
    fi
  done

  if ! sudo apt-get -y install \
      --no-install-recommends \
      "${LIBRESPOT_BUILD_DEPENDENCIES[@]}"; then
    if ! _spotify_cleanup_build_dependencies; then
      print_lc "  Warning: failed to remove librespot build dependencies."
    fi
    exit_on_error "Failed to install librespot build dependencies."
  fi
}

_spotify_runtime_package_owners() {
  local binary="${HOME_PATH}/.local/bin/librespot"
  [[ -x "${binary}" ]] || return

  local library
  local owner
  while IFS= read -r library; do
    owner="$(dpkg-query -S "${library}" 2>/dev/null | head -n 1)"
    if [[ -z "${owner}" ]]; then
      library="$(readlink -f "${library}")"
      owner="$(dpkg-query -S "${library}" 2>/dev/null | head -n 1)"
    fi
    if [[ -n "${owner}" ]]; then
      printf '%s\n' "${owner%%: /*}"
    fi
  done < <(
    ldd "${binary}" \
      | awk '$2 == "=>" && $3 ~ /^\// { print $3 }
             $1 ~ /^\// { print $1 }'
  )
}

_spotify_cleanup_build_dependencies() {
  if [[ "${#LIBRESPOT_BUILD_DEPENDENCIES_TO_REMOVE[@]}" -eq 0 ]]; then
    return
  fi

  print_lc "  Remove librespot build dependencies"

  local runtime_packages=()
  local package
  while IFS= read -r package; do
    [[ -n "${package}" ]] && runtime_packages+=("${package}")
  done < <(_spotify_runtime_package_owners | sort -u)

  if [[ "${#runtime_packages[@]}" -gt 0 ]]; then
    sudo apt-mark manual "${runtime_packages[@]}" >/dev/null || return 1
  fi

  sudo apt-get -y purge \
    "${LIBRESPOT_BUILD_DEPENDENCIES_TO_REMOVE[@]}" || return 1
  sudo apt-get -y autoremove --purge || return 1
}

_spotify_install_librespot_from_source() {
  print_lc "  Build librespot ${LIBRESPOT_VERSION} (${LIBRESPOT_REVISION:0:8})"
  _spotify_install_build_dependencies

  local cargo_tmp_dir
  mkdir -p "${HOME_PATH}/.cache" \
    || exit_on_error "Failed to create the librespot build directory."
  cargo_tmp_dir="$(mktemp -d "${HOME_PATH}/.cache/librespot-build.XXXXXX")" \
    || exit_on_error "Failed to create the librespot build directory."

  # Raspberry Pi OS mounts /tmp as a small tmpfs. Build on persistent storage.
  if ! CARGO_HOME="${cargo_tmp_dir}/cargo-home" \
      TMPDIR="${cargo_tmp_dir}" cargo install librespot \
      --git "${LIBRESPOT_REPOSITORY}" \
      --rev "${LIBRESPOT_REVISION}" \
      --locked \
      --force \
      --root "${HOME_PATH}/.local" \
      --no-default-features \
      --features native-tls,pulseaudio-backend,with-libmdns; then
    rm -rf "${cargo_tmp_dir}"
    if ! _spotify_cleanup_build_dependencies; then
      print_lc "  Warning: failed to remove librespot build dependencies."
    fi
    exit_on_error "Failed to compile and install librespot."
  fi

  rm -rf "${cargo_tmp_dir}"
  _spotify_cleanup_build_dependencies \
    || exit_on_error "Failed to remove librespot build dependencies."
}

_spotify_install_librespot() {
  print_lc "  Install librespot ${LIBRESPOT_VERSION} (${LIBRESPOT_BUILD_ID})"

  if _spotify_install_prebuilt_librespot; then
    return
  fi

  if [[ "${LIBRESPOT_ALLOW_SOURCE_BUILD:-false}" == true ]]; then
    print_lc "  No valid prebuilt librespot archive found; source build was explicitly enabled."
    _spotify_install_librespot_from_source
    return
  fi

  local architecture
  architecture=$(_spotify_librespot_architecture 2>/dev/null || printf unknown)
  exit_on_error "No valid prebuilt librespot archive is available for ${architecture}.
Publish the '${LIBRESPOT_RELEASE_TAG}' assets from:
https://github.com/${GIT_USER}/${GIT_REPO_NAME}/actions/workflows/build_librespot.yml
Then rerun the installation. To compile locally instead, explicitly set
LIBRESPOT_ALLOW_SOURCE_BUILD=true."
}

_spotify_append_finish_message() {
  local message="Spotify is enabled. After reboot, select '${SPOTIFY_DEVICE_NAME}'
once in an official Spotify app."

  if [[ "${SPOTIFY_REDIRECT_URI}" == "${SPOTIFY_DEFAULT_REDIRECT_URI}" ]]; then
    message="${message}

To connect the Spotify Web API, run this on the computer where you
will open the Phoniebox Web App:
ssh -L 3000:127.0.0.1:80 ${CURRENT_USER:-USER}@$(hostname).local
Keep the SSH session open, browse to http://127.0.0.1:3000, then
select Settings > Spotify > Connect."
  else
    message="${message}
Then open the Web App at the origin configured for
${SPOTIFY_REDIRECT_URI}
and select Settings > Spotify > Connect."
  fi

  FIN_MESSAGE="${FIN_MESSAGE:+$FIN_MESSAGE\n}${message}"
}

_spotify_configure() {
  print_lc "  Configure Spotify services"

  mkdir -p "${HOME_PATH}/.cache/librespot"
  python "${INSTALLATION_PATH}/installation/components/configure_spotify.py" \
    "${SETTINGS_PATH}/jukebox.yaml" \
    --client-id "${SPOTIFY_CLIENT_ID}" \
    --redirect-uri "${SPOTIFY_REDIRECT_URI}" \
    --device-name "${SPOTIFY_DEVICE_NAME}"

  sudo cp -f \
    "${INSTALLATION_PATH}/resources/default-services/librespot.service" \
    "${LIBRESPOT_SERVICE_PATH}"
  sudo sed -i \
    "s|%%SPOTIFY_DEVICE_NAME%%|${SPOTIFY_DEVICE_NAME}|g" \
    "${LIBRESPOT_SERVICE_PATH}"
  sudo mkdir -p "${JUKEBOX_SPOTIFY_DROPIN_DIR}"
  sudo cp -f \
    "${INSTALLATION_PATH}/resources/default-services/jukebox-spotify.conf" \
    "${JUKEBOX_SPOTIFY_DROPIN}"
  sudo chmod 644 "${LIBRESPOT_SERVICE_PATH}" "${JUKEBOX_SPOTIFY_DROPIN}"

  systemctl --user daemon-reload
  systemctl --user enable librespot.service

  _spotify_append_finish_message
}

_spotify_check() {
  print_verify_installation

  verify_apt_packages ca-certificates libpulse0 libssl3t64
  "${HOME_PATH}/.local/bin/librespot" --version \
    || exit_on_error "The librespot binary cannot be executed."
  verify_files_chown "${CURRENT_USER}" "${CURRENT_USER_GROUP}" \
    "${HOME_PATH}/.local/bin/librespot"
  verify_dirs_chown "${CURRENT_USER}" "${CURRENT_USER_GROUP}" \
    "${HOME_PATH}/.cache/librespot"
  verify_files_chown root root \
    "${LIBRESPOT_SERVICE_PATH}" \
    "${JUKEBOX_SPOTIFY_DROPIN}"
  verify_file_contains_string "backend pulseaudio" "${LIBRESPOT_SERVICE_PATH}"
  verify_file_contains_string "enabled: true" "${SETTINGS_PATH}/jukebox.yaml"
  verify_service_enablement librespot.service enabled --user
}

_run_setup_spotify() {
  _spotify_validate_configuration
  _spotify_enable_ipv6
  _spotify_install_librespot
  _spotify_configure
  _spotify_check
}

setup_spotify() {
  if [[ "${SETUP_SPOTIFY}" != true ]]; then
    return
  fi
  if [[ "$(get_architecture)" == "armv6" ]]; then
    print_lc "Spotify is not yet supported on ARMv6; continuing without Spotify support."
    SETUP_SPOTIFY=false
    return
  fi
  run_with_log_frame _run_setup_spotify "Install Spotify support"
}
