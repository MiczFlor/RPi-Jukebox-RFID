FROM arm32v7/debian:buster-slim

# Prepare Raspberry Pi like environment

# These are only dependencies that are required to get as close to the
# Raspberry Pi environment as possible.
RUN apt-get update && apt-get install -y \
    libasound2-dev \
    pulseaudio \
    pulseaudio-utils \
    --no-install-recommends \
    && rm -rf /var/lib/apt/lists/*

ARG UID
ARG USER
ARG HOME
ENV INSTALLATION_PATH ${HOME}/RPi-Jukebox-RFID

RUN test ${UID} -gt 0 && useradd -m -u ${UID} ${USER} || continue
RUN usermod -aG pulse ${USER}

# Jukebox
# Install all Jukebox dependencies
RUN apt-get update && apt-get install -qq -y \
    --allow-downgrades --allow-remove-essential --allow-change-held-packages \
    at wget gcc \
    mpc mpg123 git ffmpeg spi-tools netcat alsa-tools \
    python3 python3-venv python3-dev python3-mutagen
#samba samba-common-bin
#raspberrypi-kernel-headers
#resolvconf

# Install Jukebox
# Install libzmq with Websocket support from pre-compiled source
ENV ZMQ_TMP_DIR "/root/libzmq"
ENV ZMQ_PREFIX "/usr/local"
ENV ZMQ_DRAFT_API 1
RUN mkdir -p ${ZMQ_TMP_DIR} && cd ${ZMQ_TMP_DIR}; \
    wget --quiet --load-cookies /tmp/cookies.txt "https://docs.google.com/uc?export=download&confirm=$(wget --quiet --save-cookies /tmp/cookies.txt --keep-session-cookies --no-check-certificate 'https://docs.google.com/uc?export=download&id=1KP6BqLF-i2dCUsHhOUpOwwuOmKsB5GKY' -O- | sed -rn 's/.*confirm=([0-9A-Za-z_]+).*/\1\n/p')&id=1KP6BqLF-i2dCUsHhOUpOwwuOmKsB5GKY" -O libzmq.tar.gz && rm -rf /tmp/cookies.txt; \
    tar -xzf libzmq.tar.gz; \
    rm -f libzmq.tar.gz; \
    cp -rf * ${ZMQ_PREFIX}/

# Install libzmq with Websocket and compile
# ENV LIBSODIUM_VERSION 1.0.18
# ENV ZMQ_VERSION 4.3.4
# RUN mkdir -p ${ZMQ_TMP_DIR} && cd ${ZMQ_TMP_DIR}; \
#     wget --quiet https://github.com/jedisct1/libsodium/releases/download/${LIBSODIUM_VERSION}-RELEASE/libsodium-${LIBSODIUM_VERSION}.tar.gz; \
#     tar -zxvf libsodium-${LIBSODIUM_VERSION}.tar.gz; \
#     cd libsodium-${LIBSODIUM_VERSION}/; \
#     ./configure; \
#     make && make install
# RUN cd ${ZMQ_TMP_DIR}; \
#     wget https://github.com/zeromq/libzmq/releases/download/v${ZMQ_VERSION}/zeromq-${ZMQ_VERSION}.tar.gz -O libzmq.tar.gz; \
#     tar -xzf libzmq.tar.gz; \
#     zeromq-${ZMQ_VERSION}/configure --prefix=${ZMQ_PREFIX} --enable-drafts; \
#     make && make install;

ENV VIRTUAL_ENV=${INSTALLATION_PATH}/.venv
RUN python3 -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

USER ${USER}
WORKDIR ${HOME}
COPY --chown=${USER}:${USER} . ${INSTALLATION_PATH}/

RUN pip install --no-cache-dir -r ${INSTALLATION_PATH}/requirements.txt
RUN pip install --no-cache-dir --no-binary pyzmq pyzmq

EXPOSE 5555 5556

WORKDIR ${INSTALLATION_PATH}/src/jukebox

# Run Jukebox
# CMD bash
CMD python ${INSTALLATION_PATH}/src/jukebox/run_jukebox.py
