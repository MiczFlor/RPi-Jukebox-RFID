FROM debian:buster-slim

# Prepare Raspberry Pi like environment

# These are only dependencies that are required to get as close to the
# Raspberry Pi environment as possible. They don't include Jukebox
# specific dependencies. They will be installed in a separate install script
RUN apt-get update && apt-get install -y \
    alsa-utils \
    libasound2-dev \
    libasound2-plugins \
    pulseaudio \
    pulseaudio-utils \
    --no-install-recommends \
    && rm -rf /var/lib/apt/lists/*
 
RUN usermod -aG audio,pulse,pulse-access root

ENV HOME /root
ENV MPD_HOST mpd
ENV INSTALLATION_DIR /home/pi/RPi-Jukebox-RFID
ENV DEV_FOLDER ${INSTALLATION_DIR}/docker-development

WORKDIR $INSTALLATION_DIR

# Jukebox
# Install all Jukebox dependencies
RUN apt-get update && apt-get install -qq -y \
    --allow-downgrades --allow-remove-essential --allow-change-held-packages \
    gcc lighttpd php7.3-common php7.3-cgi php7.3 php-zmq at \
    mpc mpg123 git ffmpeg spi-tools netcat alsa-tools \
    python3 python3-dev python3-pip python3-mutagen python3-gpiozero
#samba samba-common-bin
#raspberrypi-kernel-headers
#resolvconf
#python3-spidev

RUN update-alternatives --install /usr/bin/python python /usr/bin/python3.7 1

COPY . ${INSTALLATION_DIR}
COPY ./misc/audiofiletype02.wav ./shared/startupsound.wav

# Install Jukebox
RUN pip3 install --no-cache-dir -r ${INSTALLATION_DIR}/Phoniebox/requirements.txt
RUN chmod +x ${DEV_FOLDER}/install-jukebox.sh ${DEV_FOLDER}/start-jukebox.sh
RUN ${DEV_FOLDER}/install-jukebox.sh

# Run Jukebox
# CMD ${DEV_FOLDER}/start-jukebox.sh
CMD bash
