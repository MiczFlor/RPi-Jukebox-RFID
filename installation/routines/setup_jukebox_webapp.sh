#!/usr/bin/env bash

setup_jukebox_webapp() {
  echo "Install web application" | tee /dev/fd/3

  # Install Node
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

    # Slower PIs need this to finish building the Webapp
    MEMORY=`cat /proc/meminfo | awk '$1 == "MemTotal:" {print 0+$2}'`
    if [[ $MEMORY -lt 1024000 ]]
    then
      export NODE_OPTIONS=--max-old-space-size=1024
    fi

    if [[ $MEMORY -lt 512000 ]]
    then
      export NODE_OPTIONS=--max-old-space-size=512
    fi
  fi

  # Install Node dependencies
  # TODO: Avoid building the app locally
  # Instead implement a Github Action that prebuilds on commititung a git tag
  echo "  Building web application"
  cd ${INSTALLATION_PATH}/src/webapp
  npm ci --prefer-offline --no-audit --production
  rm -rf build
  npm run build

  echo "  Register Webapp system service" | tee /dev/fd/3
  sudo cp -f ${INSTALLATION_PATH}/resources/default-services/jukebox-webapp.service ${SYSTEMD_PATH}
  sudo chmod 644 ${SYSTEMD_PATH}/jukebox-webapp.service

  sudo systemctl enable jukebox-webapp.service
  sudo systemctl daemon-reload

  echo "DONE: setup_jukebox_webapp"
}
