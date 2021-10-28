#!/usr/bin/env bash

# Constants
GD_ID_COMPILED_WEBAPP="1Dp04fBkMrfc6LT0NBG9hjItUDSjrhRh0" # https://drive.google.com/file/d/1Dp04fBkMrfc6LT0NBG9hjItUDSjrhRh0/view?usp=sharing

# For ARMv7+
NODE_SOURCE="https://deb.nodesource.com/setup_16.x"
# For ARMv6
# To update version, follow these links
# https://github.com/sdesalas/node-pi-zero
# https://github.com/nodejs/unofficial-builds/
NODE_SOURCE_EXPERIMENTAL="https://raw.githubusercontent.com/sdesalas/node-pi-zero/master/install-node-v16.3.0.sh"

# Slower PIs need this to finish building the Webapp
_jukebox_webapp_export_node_memory_limit() {
  export NODE_OPTIONS=--max-old-space-size=512
  echo "NODE_OPTIONS set to: '${NODE_OPTIONS}'"
}

_jukebox_webapp_install_node() {
  sudo apt-get -y update

  if which node > /dev/null; then
    echo "  Found existing NodeJS. Hence, updating NodeJS"
    sudo npm cache clean -f
    sudo npm install --silent -g n
    sudo n --quiet latest
    sudo npm update --silent -g
  else
    echo "  Install NodeJS"

    # Zero and older versions of Pi with ARMv6 only
    # support experimental NodeJS
    if [ `uname -m` = "armv6l" ]; then
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
  cd ${INSTALLATION_PATH}/src/webapp
  npm ci --prefer-offline --no-audit --production
  rm -rf build
  npm run build
}

_jukebox_webapp_download() {
  echo "  Downloading web application"
  local TAR_FILENAME="webapp-build.tar.gz"
  cd ${INSTALLATION_PATH}/src/webapp
  _download_file_from_google_drive ${GD_ID_COMPILED_WEBAPP} ${TAR_FILENAME}
  tar -xzf ${TAR_FILENAME}
  rm -f ${TAR_FILENAME}
  cd ${INSTALLATION_PATH}
}

_jukebox_webapp_register_as_system_service_with_nginx() {
  echo "  Install and configure nginx"
  sudo apt-get -qq -y update
  sudo apt-get -y purge apache2
  sudo apt-get -y install nginx

  sudo service nginx start

  sudo mv -f /etc/nginx/sites-available/default /etc/nginx/sites-available/default.orig
  sudo cp -f ${INSTALLATION_PATH}/resources/default-settings/nginx.default /etc/nginx/sites-available/default

  sudo service nginx restart
}


setup_jukebox_webapp() {
  echo "Install web application" | tee /dev/fd/3

  if [ "$ENABLE_WEBAPP_PROD_BUILD" = true ] ; then
    _jukebox_webapp_download
  else
    _jukebox_webapp_export_node_memory_limit
    _jukebox_webapp_install_node
    _jukebox_webapp_build
  fi
  _jukebox_webapp_register_as_system_service_with_nginx

  echo "DONE: setup_jukebox_webapp"
}
