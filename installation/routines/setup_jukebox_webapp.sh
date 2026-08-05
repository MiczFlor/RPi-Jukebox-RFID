#!/usr/bin/env bash

# Constants
WEBAPP_NGINX_SITE_DEFAULT_CONF="/etc/nginx/sites-available/default"
WEBAPP_DEVELOPMENT_RELEASE_TAG="webapp-development"

_jukebox_webapp_try_download() {
  local download_url="$1"
  local tar_filename="$2"

  print_lc "    Checking ${download_url}"
  if ! validate_url "${download_url}"; then
    log "    Web App bundle not found: ${download_url}"
    return 1
  fi

  print_lc "    Using Web App bundle: ${download_url}"
  download_from_url "${download_url}" "${tar_filename}"
}

_jukebox_webapp_download() {
  print_lc "  Downloading Web App"
  local jukebox_version
  local git_head_hash
  local git_head_hash_short
  local git_user_normalized
  local git_upstream_user_normalized
  local tar_filename="webapp-build.tar.gz"
  local bundle_name
  local source_development_url
  local source_release_url
  local upstream_development_url
  local upstream_release_url
  local bundle_downloaded=false

  jukebox_version=$(python "${INSTALLATION_PATH}/src/jukebox/jukebox/version.py") \
    || exit_on_error "Could not determine the Jukebox version"
  git_head_hash=$(git -C "${INSTALLATION_PATH}" rev-parse --verify --quiet HEAD) \
    || exit_on_error "Could not determine the installed commit"
  git_head_hash_short=${git_head_hash:0:10}
  bundle_name="webapp-build-${git_head_hash_short}.tar.gz"
  source_development_url="https://github.com/${GIT_USER}/${GIT_REPO_NAME}/releases/download/${WEBAPP_DEVELOPMENT_RELEASE_TAG}/${bundle_name}"
  source_release_url="https://github.com/${GIT_USER}/${GIT_REPO_NAME}/releases/download/v${jukebox_version}/${bundle_name}"
  upstream_development_url="https://github.com/${GIT_UPSTREAM_USER}/${GIT_REPO_NAME}/releases/download/${WEBAPP_DEVELOPMENT_RELEASE_TAG}/${bundle_name}"
  upstream_release_url="https://github.com/${GIT_UPSTREAM_USER}/${GIT_REPO_NAME}/releases/download/v${jukebox_version}/${bundle_name}"
  git_user_normalized=$(printf '%s' "${GIT_USER}" | tr '[:upper:]' '[:lower:]')
  git_upstream_user_normalized=$(printf '%s' "${GIT_UPSTREAM_USER}" | tr '[:upper:]' '[:lower:]')

  cd "${INSTALLATION_PATH}/src/webapp" || exit_on_error

  if [[ "$ENABLE_WEBAPP_PROD_DOWNLOAD" != "release-only" ]] \
      && _jukebox_webapp_try_download "${source_development_url}" "${tar_filename}"; then
    bundle_downloaded=true
  elif _jukebox_webapp_try_download "${source_release_url}" "${tar_filename}"; then
    bundle_downloaded=true
  elif [[ "${git_user_normalized}" != "${git_upstream_user_normalized}" ]] \
      && _jukebox_webapp_try_download "${upstream_development_url}" "${tar_filename}"; then
    bundle_downloaded=true
  elif [[ "${git_user_normalized}" != "${git_upstream_user_normalized}" ]] \
      && _jukebox_webapp_try_download "${upstream_release_url}" "${tar_filename}"; then
    bundle_downloaded=true
  fi

  if [[ "$bundle_downloaded" != true ]]; then
    cd "${INSTALLATION_PATH}" || exit_on_error
    return 1
  fi

  tar -xzf "${tar_filename}" || exit_on_error "Invalid Web App bundle"
  rm -f "${tar_filename}"
  cd "${INSTALLATION_PATH}" || exit_on_error
}

_jukebox_webapp_register_as_system_service_with_nginx() {
  print_lc "  Configure nginx"

  sudo mv -f "${WEBAPP_NGINX_SITE_DEFAULT_CONF}" "${WEBAPP_NGINX_SITE_DEFAULT_CONF}.orig"
  sudo cp -f "${INSTALLATION_PATH}/resources/default-settings/nginx.default" "${WEBAPP_NGINX_SITE_DEFAULT_CONF}"
  sudo sed -i "s|%%INSTALLATION_PATH%%|${INSTALLATION_PATH}|g" "${WEBAPP_NGINX_SITE_DEFAULT_CONF}"

  if [ "$DISABLE_IPv6" = true ] ; then
    sudo sed -i '/listen \[::\]:80/d' "${WEBAPP_NGINX_SITE_DEFAULT_CONF}"
  fi

  # make sure nginx can access the home directory of the user
  sudo chmod o+x "${HOME_PATH}"

  sudo systemctl restart nginx.service
}

_jukebox_webapp_check() {
    print_verify_installation

    verify_dirs_exists "${INSTALLATION_PATH}/src/webapp/build"
    verify_apt_packages nginx
    verify_files_exists "${WEBAPP_NGINX_SITE_DEFAULT_CONF}"
    verify_file_contains_string "location = /api/v1/library/files" "${WEBAPP_NGINX_SITE_DEFAULT_CONF}"
    verify_file_contains_string "client_max_body_size 1g" "${WEBAPP_NGINX_SITE_DEFAULT_CONF}"
    verify_file_contains_string "proxy_request_buffering off" "${WEBAPP_NGINX_SITE_DEFAULT_CONF}"

    if [ "$DISABLE_IPv6" = true ] ; then
      verify_file_does_not_contain_string "listen [::]:80" "${WEBAPP_NGINX_SITE_DEFAULT_CONF}"
    fi

    verify_service_enablement nginx.service enabled
}

_run_setup_jukebox_webapp() {
    if [[ "$ENABLE_WEBAPP_PROD_DOWNLOAD" == true || "$ENABLE_WEBAPP_PROD_DOWNLOAD" == "release-only" ]] ; then
        if ! _jukebox_webapp_download; then
            local git_head_hash
            git_head_hash=$(git -C "${INSTALLATION_PATH}" rev-parse --verify --quiet HEAD) \
              || exit_on_error "Could not determine the installed commit"
            exit_on_error "No pre-built Web App bundle found for commit ${git_head_hash}.
Enable 'Test Build Web App v3' and grant Actions read/write permissions in the source repository:
https://github.com/${GIT_USER}/${GIT_REPO_NAME}/actions/workflows/test_build_webapp_v3.yml
Push this exact commit or run the workflow manually, wait for it to publish the bundle, then rerun the installation."
        fi
    elif [[ "$ENABLE_WEBAPP_PROD_DOWNLOAD" == false ]]; then
        exit_on_error "Local Web App builds were removed and ENABLE_WEBAPP_PROD_DOWNLOAD=false is unsupported.
Publish an exact-commit Web App bundle and use ENABLE_WEBAPP_PROD_DOWNLOAD=true."
    else
        exit_on_error "Invalid ENABLE_WEBAPP_PROD_DOWNLOAD value: ${ENABLE_WEBAPP_PROD_DOWNLOAD}"
    fi
    _jukebox_webapp_register_as_system_service_with_nginx
    _jukebox_webapp_check
}

setup_jukebox_webapp() {
    if [ "$ENABLE_WEBAPP" == true ] ; then
        run_with_log_frame _run_setup_jukebox_webapp "Install Web App"
    fi
}
