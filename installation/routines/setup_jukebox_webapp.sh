#!/usr/bin/env bash

# Constants
WEBAPP_NGINX_SITE_DEFAULT_CONF="/etc/nginx/sites-available/default"

# For ARMv7+
NODE_MAJOR=20
# For ARMv6
# To update version, follow these links
# https://github.com/sdesalas/node-pi-zero
# https://github.com/nodejs/unofficial-builds/
NODE_SOURCE_EXPERIMENTAL="https://raw.githubusercontent.com/sdesalas/node-pi-zero/master/install-node-v16.3.0.sh"

_jukebox_webapp_install_node() {
  sudo apt-get -y update

  if which node > /dev/null; then
    print_lc "  Found existing NodeJS. Hence, updating NodeJS"
    sudo npm cache clean -f
    sudo npm install --silent -g n
    sudo n --quiet latest
    sudo npm update --silent -g
  else
    print_lc "  Install NodeJS"

    # Zero and older versions of Pi with ARMv6 only
    # support experimental NodeJS
    if [[ $(uname -m) == "armv6l" ]]; then
      wget -O - ${NODE_SOURCE_EXPERIMENTAL} | sudo bash
      sudo apt-get -qq -y install nodejs
      sudo npm install --silent -g npm
    else
      # install NodeJS and npm as recommended in
      # https://github.com/nodesource/distributions
      sudo apt-get install -y ca-certificates curl gnupg
      sudo mkdir -p /etc/apt/keyrings
      curl -fsSL https://deb.nodesource.com/gpgkey/nodesource-repo.gpg.key | sudo gpg --dearmor -o /etc/apt/keyrings/nodesource.gpg
      echo "deb [signed-by=/etc/apt/keyrings/nodesource.gpg] https://deb.nodesource.com/node_$NODE_MAJOR.x nodistro main" | sudo tee /etc/apt/sources.list.d/nodesource.list
      sudo apt-get update
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
  sudo apt-get -qq -y update
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
        verify_apt_packages nodejs
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
