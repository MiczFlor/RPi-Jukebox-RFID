FROM debian:bullseye-slim

RUN set -eux ; \
    apt-get update && apt-get install -y \
    alsa-utils \
    libasound2-dev \
    libasound2-plugins \
    pulseaudio \
    pulseaudio-utils \
    default-jre

RUN usermod -aG audio,pulse,pulse-access root

ENV INSTALLATION_PATH /home/pi/librespot-java
ENV LIBRESPOT_JAVA_VERSION 1.6.2

WORKDIR $INSTALLATION_PATH
VOLUME $INSTALLATION_PATH

ADD https://github.com/librespot-org/librespot-java/releases/download/v${LIBRESPOT_JAVA_VERSION}/librespot-api-${LIBRESPOT_JAVA_VERSION}.jar ${INSTALLATION_PATH}

EXPOSE 12345
EXPOSE 24879

CMD java -jar librespot-api-${LIBRESPOT_JAVA_VERSION}.jar
