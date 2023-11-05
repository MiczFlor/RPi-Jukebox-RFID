#!/usr/bin/env bash

# Constants
GD_ID_COMPILED_WEBAPP="1EE_1MdneGtKL5V7GyYZC0nb6ODQWTsPb" # https://drive.google.com/file/d/1EE_1MdneGtKL5V7GyYZC0nb6ODQWTsPb/view?usp=sharing

# For ARMv7+
NODE_SOURCE="https://deb.nodesource.com/setup_16.x"
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
      NODE_SOURCE=${NODE_SOURCE_EXPERIMENTAL}
    fi

    wget -O - ${NODE_SOURCE} | sudo bash
    sudo apt-get -qq -y install nodejs
    sudo npm install --silent -g npm
  fi
}

# TODO: Avoid building the app locally
# Instead implement a Github Action that prebuilds on commititung a git tag
_jukebox_webapp_build() {
  echo "  Building web application"
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

  sudo service nginx start

  sudo mv -f /etc/nginx/sites-available/default /etc/nginx/sites-available/default.orig
  sudo cp -f "${INSTALLATION_PATH}/resources/default-settings/nginx.default" /etc/nginx/sites-available/default

  sudo service nginx restart
}

_jukebox_build_local_docs() {
  echo "  Build docs locally" | tee /dev/fd/3
  "${INSTALLATION_PATH}/run_sphinx.sh" -c
}


setup_jukebox_webapp() {
  echo "Install web application" | tee /dev/fd/3

  if [[ $ENABLE_WEBAPP_PROD_DOWNLOAD == true || $ENABLE_WEBAPP_PROD_DOWNLOAD == release-only ]] ; then
    _jukebox_webapp_download
  fi
  if [[ $ENABLE_INSTALL_NODE == true ]] ; then
    _jukebox_webapp_install_node
    # Local Web App build during installation does not work at the moment
    # Needs to be done after reboot! There will be a message at the end of the installation process
    # _jukebox_webapp_build
  fi
  if [[ $ENABLE_LOCAL_DOCS == true ]]; then
    _jukebox_build_local_docs
  fi
  _jukebox_webapp_register_as_system_service_with_nginx

  echo "DONE: setup_jukebox_webapp"
}
