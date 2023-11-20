#!/usr/bin/env bash

# Constants
GD_ID_COMPILED_WEBAPP="1EE_1MdneGtKL5V7GyYZC0nb6ODQWTsPb" # https://drive.google.com/file/d/1EE_1MdneGtKL5V7GyYZC0nb6ODQWTsPb/view?usp=sharing
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
    echo "  Found existing NodeJS. Hence, updating NodeJS" | tee /dev/fd/3
    sudo npm cache clean -f
    sudo npm install --silent -g n
    sudo n --quiet latest
    sudo npm update --silent -g
  else
    echo "  Install NodeJS" | tee /dev/fd/3

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

# TODO: Avoid building the app locally
# Instead implement a Github Action that prebuilds on commititung a git tag
_jukebox_webapp_build() {
  echo "  Building web application" | tee /dev/fd/3
  cd "${INSTALLATION_PATH}/src/webapp" || exit_on_error
  npm ci --prefer-offline --no-audit --production
  rm -rf build
  # The build wrapper script checks available memory on system and sets Node options accordingly
  ./run_rebuild.sh
}

_jukebox_webapp_download() {
  echo "  Downloading web application" | tee /dev/fd/3
  local TAR_FILENAME="webapp-build.tar.gz"
  cd "${INSTALLATION_PATH}/src/webapp" || exit_on_error
  _download_file_from_google_drive ${GD_ID_COMPILED_WEBAPP} ${TAR_FILENAME}
  tar -xzf ${TAR_FILENAME}
  rm -f ${TAR_FILENAME}
  cd "${INSTALLATION_PATH}" || exit_on_error
}

_jukebox_webapp_register_as_system_service_with_nginx() {
  echo "  Install and configure nginx" | tee /dev/fd/3
  sudo apt-get -qq -y update
  sudo apt-get -y purge apache2
  sudo apt-get -y install nginx

  sudo mv -f "${WEBAPP_NGINX_SITE_DEFAULT_CONF}" "${WEBAPP_NGINX_SITE_DEFAULT_CONF}.orig"
  sudo cp -f "${INSTALLATION_PATH}/resources/default-settings/nginx.default" "${WEBAPP_NGINX_SITE_DEFAULT_CONF}"

  # make sure nginx can access the home directory of the user
  sudo chmod o+x "${HOME_PATH}"

  sudo systemctl restart nginx.service
}

_jukebox_webapp_check() {
    print_verify_installation

    if [[ $ENABLE_WEBAPP_PROD_DOWNLOAD == true || $ENABLE_WEBAPP_PROD_DOWNLOAD == release-only ]] ; then
        verify_dirs_exists "${INSTALLATION_PATH}/src/webapp/build"
    fi
    if [[ $ENABLE_INSTALL_NODE == true ]] ; then
        verify_apt_packages nodejs
    fi

    verify_apt_packages nginx
    verify_files_exists "${WEBAPP_NGINX_SITE_DEFAULT_CONF}"

    verify_service_enablement nginx.service enabled
}

_run_setup_jukebox_webapp() {
    if [[ $ENABLE_WEBAPP_PROD_DOWNLOAD == true || $ENABLE_WEBAPP_PROD_DOWNLOAD == release-only ]] ; then
        _jukebox_webapp_download
    fi
    if [[ $ENABLE_INSTALL_NODE == true ]] ; then
        _jukebox_webapp_install_node
        # Local Web App build during installation does not work at the moment
        # Needs to be done after reboot! There will be a message at the end of the installation process
        # _jukebox_webapp_build
    fi
    _jukebox_webapp_register_as_system_service_with_nginx
    _jukebox_webapp_check
}

setup_jukebox_webapp() {
    if [ "$ENABLE_WEBAPP" == true ] ; then
        run_with_log_frame _run_setup_jukebox_webapp "Install web application"
    fi
}
