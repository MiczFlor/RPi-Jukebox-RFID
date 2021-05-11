FROM debian:buster-slim

RUN apt-get update && apt-get install -qq -y \
    --allow-downgrades --allow-remove-essential --allow-change-held-packages \
    gcc lighttpd php7.3-common php7.3-cgi php7.3 php-zmq at

ENV HOME /root
ENV INSTALLATION_DIR /home/pi/RPi-Jukebox-RFID
ENV DEV_FOLDER ${INSTALLATION_DIR}/docker-development

WORKDIR $INSTALLATION_DIR

COPY . ${INSTALLATION_DIR}

RUN chmod +x ${DEV_FOLDER}/start-webui.sh

COPY ./resources/sampleconfigs/lighttpd.conf.buster-default.sample /etc/lighttpd/lighttpd.conf
COPY ./resources/sampleconfigs/15-fastcgi-php.conf.buster-default.sample /etc/lighttpd/conf-available/15-fastcgi-php.conf
COPY ./resources/sampleconfigs/php.ini.buster-default.sample /etc/php/7.3/cgi/php.ini
RUN mkdir ${INSTALLATION_DIR}/htdocs && \
    chown -R root:www-data ${INSTALLATION_DIR}/htdocs && \
    chmod -R 750 ${INSTALLATION_DIR}/htdocs

CMD ${DEV_FOLDER}/start-webui.sh && /bin/bash
