FROM debian:buster-slim

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
ENV INSTALLATION_PATH /home/pi/RPi-Jukebox-RFID

WORKDIR $INSTALLATION_PATH

# Jukebox
# Install all Jukebox dependencies
RUN apt-get update && apt-get install -qq -y \
    --allow-downgrades --allow-remove-essential --allow-change-held-packages \
    gcc at wget \
    mpc mpg123 git ffmpeg spi-tools netcat alsa-tools \
    python3 python3-dev python3-pip python3-mutagen python3-gpiozero
#samba samba-common-bin
#raspberrypi-kernel-headers
#resolvconf
#python3-spidev

RUN update-alternatives --install /usr/bin/python python /usr/bin/python3 1

COPY . ${INSTALLATION_PATH}

# Install Jukebox
# Install libzmq with Websocket support from pre-compiled source
ENV ZMQ_TMP_DIR libzmq
ENV ZMQ_VERSION 4.3.4
ENV ZMQ_PREFIX /usr/local

# Compile ZMQ
RUN cd ${HOME} && mkdir ${ZMQ_TMP_DIR} && cd ${ZMQ_TMP_DIR}; \
    # wget https://github.com/zeromq/libzmq/archive/refs/heads/master.tar.gz -O libzmq.tar.gz; \
    wget https://github.com/zeromq/libzmq/releases/download/v${ZMQ_VERSION}/zeromq-${ZMQ_VERSION}.tar.gz -O libzmq.tar.gz; \
    tar -xzf libzmq.tar.gz; \
    rm -f libzmq.tar.gz; \
    zeromq-${ZMQ_VERSION}/configure --prefix=${ZMQ_PREFIX} --enable-drafts; \
    make && make install

RUN pip3 install --pre pyzmq \
    --install-option=--enable-drafts \
    --install-option=--zmq=${ZMQ_PREFIX}; \
    pip3 install --no-cache-dir -r ${INSTALLATION_PATH}/requirements.txt

EXPOSE 5555 5556

# Run Jukebox
# CMD bash
CMD python ${INSTALLATION_PATH}/src/jukebox/run_jukebox.py
