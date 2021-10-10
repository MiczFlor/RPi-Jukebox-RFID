#!/usr/bin/env bash

# Slower PIs need this to finish building the Webapp
_jukebox_webapp_export_node_memory_limit() {
  export NODE_OPTIONS=--max-old-space-size=512
  echo "NODE_OPTIONS set to: '${NODE_OPTIONS}'"
}

_jukebox_webapp_install_node() {
  if which node > /dev/null; then
    echo "  Found existing NodeJS. Hence, updating NodeJS"
    sudo npm cache clean -f
    sudo npm install --silent -g n
    sudo n --quiet latest
    sudo npm update --silent -g
  else
    echo "  Install NodeJS"
    curl -sL https://deb.nodesource.com/setup_16.x | sudo -E bash -
    sudo apt-get -qq -y install nodejs
    sudo npm install --silent -g npm serve
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

_jukebox_webapp_register_as_system_service() {
  echo "  Register Webapp system service"
  sudo cp -f ${INSTALLATION_PATH}/resources/default-services/jukebox-webapp.service ${SYSTEMD_PATH}
  sudo chmod 644 ${SYSTEMD_PATH}/jukebox-webapp.service

  sudo systemctl enable jukebox-webapp.service
  sudo systemctl daemon-reload
}

setup_jukebox_webapp() {
  echo "Install web application" | tee /dev/fd/3

  _jukebox_webapp_export_node_memory_limit
  _jukebox_webapp_install_node
  _jukebox_webapp_build
  _jukebox_webapp_register_as_system_service

  echo "DONE: setup_jukebox_webapp"
}
