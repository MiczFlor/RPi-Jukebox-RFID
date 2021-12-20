#!/usr/bin/env bash

# Constants
LIBRESPOT_JAVA_VERSION="1.6.1"
LIBRESPOT_JAVA_JAR="librespot-api-${LIBRESPOT_JAVA_VERSION}.jar"
LIBRESPOT_JAVA_API_URL="https://github.com/librespot-org/librespot-java/releases/download/v${LIBRESPOT_JAVA_VERSION}/${LIBRESPOT_JAVA_JAR}"


_install_packages() {
    echo "Installing openjdk-11-jre package to be able to run librespot-java"
    sudo apt-get -y install openjdk-11-jre
}

_download_jar() {
    echo "Downloading API jar from github"
    wget -O "${SHARED_PATH}/spotify/${LIBRESPOT_JAVA_JAR}" "${LIBRESPOT_JAVA_API_URL}"
}

_configure_librespot_java() {
    echo "Placing config file and inserting username and password"
    SPOTIFY_CONFIG_FILE="${SHARED_PATH}/spotify/config.toml"
    cp "${INSTALLATION_PATH}"/resources/default-settings/spotify.config.toml "${SPOTIFY_CONFIG_FILE}"
    sed -i "s/HERE_USERNAME/${SPOTIFY_USERNAME}/g" "${SPOTIFY_CONFIG_FILE}"
    sed -i "s/HERE_PASSWORD/${SPOTIFY_PASSWORD}/g" "${SPOTIFY_CONFIG_FILE}"
}

_install_service() {
    echo "Installing jukebox-spotify service"
    SPOTIFY_SERVICE_RESOURCE="${INSTALLATION_PATH}/resources/default-services/jukebox-spotify.service"
    sed -i "s#HERE_DIR#${SHARED_PATH}/spotify#g" "${SPOTIFY_SERVICE_RESOURCE}"
    sed -i "s#HERE_JAR_FILE#${SHARED_PATH}/spotify/${LIBRESPOT_JAVA_JAR}#g" "${SPOTIFY_SERVICE_RESOURCE}"

    sudo cp -f "${SPOTIFY_SERVICE_RESOURCE}" "${SYSTEMD_PATH}"
    sudo chmod 644 "${SYSTEMD_PATH}"/jukebox-spotify.service

    sudo systemctl enable jukebox-spotify.service
    sudo systemctl daemon-reload
}

setup_spotify() {
    echo "Install Spotify functionality" | tee /dev/fd/3

    _install_packages
    _download_jar
    _configure_librespot_java
    _install_service

    echo "DONE: setup_spotify"
}
