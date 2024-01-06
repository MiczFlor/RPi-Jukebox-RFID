#!/usr/bin/env bash

# Constants
WEBAPP_NGINX_SITE_DEFAULT_CONF="/etc/nginx/sites-available/default"

# Node major version used.
# If changed also update in .github\actions\build-webapp\action.yml
NODE_MAJOR=20
# Node version for ARMv6 (unofficial builds)
NODE_ARMv6_VERSION=v20.10.0

_jukebox_webapp_install_node() {
    print_lc "  Install NodeJS"

    local node_installed=$(node -v)
    local arch=$(uname -m)
    if [[ "$arch" == "armv6l" ]]; then
        if [ "$node_installed" == "$NODE_ARMv6_VERSION" ]; then
            print_lc "    Skipping. NodeJS already installed"
        else
            # For ARMv6 unofficial build
            # https://github.com/nodejs/unofficial-builds/
            local node_tmp_dir="${HOME_PATH}/node"
            local node_install_dir=/usr/local/lib/nodejs
            local node_filename="node-${NODE_ARMv6_VERSION}-linux-${arch}"
            local node_tar_filename="${node_filename}.tar.gz"
            node_download_url="https://unofficial-builds.nodejs.org/download/release/${NODE_ARMv6_VERSION}/${node_tar_filename}"

            mkdir -p "${node_tmp_dir}" && cd "${node_tmp_dir}" || exit_on_error
            download_from_url ${node_download_url} ${node_tar_filename}
            tar -xzf ${node_tar_filename}
            rm -rf ${node_tar_filename}

            # see https://github.com/nodejs/help/wiki/Installation
            # Remove existing symlinks
            sudo unlink /usr/bin/node
            sudo unlink /usr/bin/npm
            sudo unlink /usr/bin/npx

            # Clear existing nodejs and copy new files
            sudo rm -rf "${node_install_dir}"
            sudo mv "${node_filename}" "${node_install_dir}"

            sudo ln -s "${node_install_dir}/bin/node" /usr/bin/node
            sudo ln -s "${node_install_dir}/bin/npm" /usr/bin/npm
            sudo ln -s "${node_install_dir}/bin/npx" /usr/bin/npx

            cd "${HOME_PATH}" || exit_on_error
            rm -rf "${node_tmp_dir}"
        fi
    else
        if [[ "$node_installed" == "v${NODE_MAJOR}."* ]]; then
            print_lc "    Skipping. NodeJS already installed"
        else
            sudo apt-get remove -y nodejs
            # install NodeJS as recommended in
            # https://github.com/nodesource/distributions
            curl -fsSL https://deb.nodesource.com/setup_${NODE_MAJOR}.x | sudo bash - &&\
            sudo apt-get install -y nodejs
        fi
    fi
}

_jukebox_webapp_build() {
  print_lc "  Building Web App"
  cd "${INSTALLATION_PATH}/src/webapp" || exit_on_error
  ./run_rebuild.sh -u
}

_jukebox_webapp_download() {
  print_lc "  Downloading Web App"
  local jukebox_version=$(python "${INSTALLATION_PATH}/src/jukebox/jukebox/version.py")
  local git_head_hash=$(git -C "${INSTALLATION_PATH}" rev-parse --verify --quiet HEAD)
  local git_head_hash_short=${git_head_hash:0:10}
  local tar_filename="webapp-build.tar.gz"
  # URL must be set to default repo as installation can be run from different repos as well where releases may not exist
  local download_url_commit="https://github.com/${GIT_UPSTREAM_USER}/RPi-Jukebox-RFID/releases/download/v${jukebox_version}/webapp-build-${git_head_hash_short}.tar.gz"
  local download_url_latest="https://github.com/${GIT_UPSTREAM_USER}/RPi-Jukebox-RFID/releases/download/v${jukebox_version}/webapp-build-latest.tar.gz"

  cd "${INSTALLATION_PATH}/src/webapp" || exit_on_error
  if validate_url ${download_url_commit} ; then
    log "    DOWNLOAD_URL ${download_url_commit}"
    download_from_url ${download_url_commit} ${tar_filename}
  elif [[ "$ENABLE_WEBAPP_PROD_DOWNLOAD" == true ]] && validate_url ${download_url_latest} ; then
    log "    DOWNLOAD_URL ${download_url_latest}"
    download_from_url ${download_url_latest} ${tar_filename}
  else
    exit_on_error "No prebuild Web App bundle found!"
  fi
  tar -xzf ${tar_filename}
  rm -f ${tar_filename}
  cd "${INSTALLATION_PATH}" || exit_on_error
}

_jukebox_webapp_register_as_system_service_with_nginx() {
  print_lc "  Install and configure nginx"
  sudo apt-get -y update
  sudo apt-get -y purge apache2
  sudo apt-get -y install nginx

  sudo mv -f "${WEBAPP_NGINX_SITE_DEFAULT_CONF}" "${WEBAPP_NGINX_SITE_DEFAULT_CONF}.orig"
  sudo cp -f "${INSTALLATION_PATH}/resources/default-settings/nginx.default" "${WEBAPP_NGINX_SITE_DEFAULT_CONF}"
  sudo sed -i "s|%%INSTALLATION_PATH%%|${INSTALLATION_PATH}|g" "${WEBAPP_NGINX_SITE_DEFAULT_CONF}"

  # make sure nginx can access the home directory of the user
  sudo chmod o+x "${HOME_PATH}"

  sudo systemctl restart nginx.service
}

_jukebox_webapp_check() {
    print_verify_installation

    if [[ "$ENABLE_WEBAPP_PROD_DOWNLOAD" == true || "$ENABLE_WEBAPP_PROD_DOWNLOAD" == "release-only" ]] ; then
        verify_dirs_exists "${INSTALLATION_PATH}/src/webapp/build"
    else
        local arch=$(uname -m)
        if [[ "$arch" == "armv6l" ]]; then
            local node_installed=$(node -v)
            log "  Verify 'node' is installed"
            test ! "${node_installed}" == "${NODE_ARMv6_VERSION}" && exit_on_error "ERROR: 'node' not in expected version: '${node_installed}' instead of '${NODE_ARMv6_VERSION}'!"
            log "  CHECK"
        else
            verify_apt_packages nodejs
        fi

        verify_dirs_exists "${INSTALLATION_PATH}/src/webapp/build"
    fi

    verify_apt_packages nginx
    verify_files_exists "${WEBAPP_NGINX_SITE_DEFAULT_CONF}"

    verify_service_enablement nginx.service enabled
}

_run_setup_jukebox_webapp() {
    if [[ "$ENABLE_WEBAPP_PROD_DOWNLOAD" == true || "$ENABLE_WEBAPP_PROD_DOWNLOAD" == "release-only" ]] ; then
        _jukebox_webapp_download
    else
        _jukebox_webapp_install_node
        _jukebox_webapp_build
    fi
    _jukebox_webapp_register_as_system_service_with_nginx
    _jukebox_webapp_check
}

setup_jukebox_webapp() {
    if [ "$ENABLE_WEBAPP" == true ] ; then
        run_with_log_frame _run_setup_jukebox_webapp "Install Web App"
    fi
}
