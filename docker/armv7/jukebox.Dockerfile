FROM arm32v7/debian:buster-slim

# Prepare Raspberry Pi like environment

# These are only dependencies that are required to get as close to the
# Raspberry Pi environment as possible.
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
    at wget gcc \
    mpc mpg123 git ffmpeg spi-tools netcat alsa-tools \
    python3 python3-dev python3-pip python3-setuptools python3-mutagen python3-gpiozero
#samba samba-common-bin
#raspberrypi-kernel-headers
#resolvconf
#python3-spidev

COPY . ${INSTALLATION_DIR}

# Install Jukebox
# Install libzmq with Websocket support from pre-compiled source
ENV ZMQ_TMP_DIR libzmq
ENV ZMQ_PREFIX /usr/local
RUN cd ${HOME} && mkdir ${ZMQ_TMP_DIR} && cd ${ZMQ_TMP_DIR}; \
    wget --quiet --load-cookies /tmp/cookies.txt "https://docs.google.com/uc?export=download&confirm=$(wget --quiet --save-cookies /tmp/cookies.txt --keep-session-cookies --no-check-certificate 'https://docs.google.com/uc?export=download&id=1KP6BqLF-i2dCUsHhOUpOwwuOmKsB5GKY' -O- | sed -rn 's/.*confirm=([0-9A-Za-z_]+).*/\1\n/p')&id=1KP6BqLF-i2dCUsHhOUpOwwuOmKsB5GKY" -O libzmq.tar.gz && rm -rf /tmp/cookies.txt; \
    tar -xzf libzmq.tar.gz; \
    rm -f libzmq.tar.gz; \
    cp -rf * ${ZMQ_PREFIX}/

# Install libzmq with Websocket and compile
# ENV LIBSODIUM_VERSION 1.0.18
# ENV ZMQ_VERSION 4.3.4
# RUN cd ${HOME} && mkdir ${ZMQ_TMP_DIR} && cd ${ZMQ_TMP_DIR}; \
#     wget --quiet https://github.com/jedisct1/libsodium/releases/download/${LIBSODIUM_VERSION}-RELEASE/libsodium-${LIBSODIUM_VERSION}.tar.gz; \
#     tar -zxvf libsodium-${LIBSODIUM_VERSION}.tar.gz; \
#     cd libsodium-${LIBSODIUM_VERSION}/; \
#     ./configure; \
#     make && make install
# RUN cd ${HOME}/${ZMQ_TMP_DIR}; \
#     wget https://github.com/zeromq/libzmq/releases/download/v${ZMQ_VERSION}/zeromq-${ZMQ_VERSION}.tar.gz -O libzmq.tar.gz; \
#     tar -xzf libzmq.tar.gz; \
#     zeromq-${ZMQ_VERSION}/configure --prefix=${ZMQ_PREFIX} --enable-drafts; \
#     make && make install;

RUN pip3 install --pre pyzmq \
        --install-option=--enable-drafts \
        --install-option=--zmq=${ZMQ_PREFIX}

RUN pip3 install --no-cache-dir -r ${INSTALLATION_DIR}/requirements.txt

EXPOSE 5555 5556

# Run Jukebox
# CMD bash
CMD python3 ${INSTALLATION_DIR}/src/jukebox/run_jukebox.py
