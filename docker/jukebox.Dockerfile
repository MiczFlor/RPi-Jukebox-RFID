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
ENV DOCKER_DIR ${INSTALLATION_DIR}/docker

WORKDIR $INSTALLATION_DIR

# Jukebox
# Install all Jukebox dependencies
RUN apt-get update && apt-get install -qq -y \
    --allow-downgrades --allow-remove-essential --allow-change-held-packages \
    gcc lighttpd at wget \
    mpc mpg123 git ffmpeg spi-tools netcat alsa-tools \
    python3 python3-dev python3-pip python3-mutagen python3-gpiozero
#samba samba-common-bin
#raspberrypi-kernel-headers
#resolvconf
#python3-spidev

RUN update-alternatives --install /usr/bin/python python /usr/bin/python3.7 1

COPY . ${INSTALLATION_DIR}

# Install Jukebox
ENV ZMQ_VERSION 4.3.4
ENV PREFIX /usr/local

RUN wget https://github.com/zeromq/libzmq/releases/download/v${ZMQ_VERSION}/zeromq-${ZMQ_VERSION}.tar.gz -O libzmq.tar.gz; \
    tar -xzf libzmq.tar.gz; \
    zeromq-${ZMQ_VERSION}/configure --prefix=${PREFIX} --enable-drafts; \
    make -j && make install; \
    pip3 install -v --pre pyzmq \
        --install-option=--enable-drafts \
        --install-option=--zmq=${PREFIX}; \
    pip3 install --no-cache-dir -r ${INSTALLATION_DIR}/requirements.txt

# RUN chmod +x ${DOCKER_DIR}/scripts/install-jukebox.sh ${DOCKER_DIR}/scripts/start-jukebox.sh
# RUN ${DOCKER_DIR}/scripts/install-jukebox.sh

# Run Jukebox
# CMD bash
EXPOSE 5555 5556

CMD python ${INSTALLATION_DIR}/src/jukebox/run_jukebox.py
