FROM debian:bullseye-slim

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

USER root
RUN test ${UID} -gt 0 && useradd -m -u ${UID} ${USER} || continue
RUN usermod -aG pulse ${USER}

# Jukebox
# Install all Jukebox dependencies
RUN apt-get update && apt-get install -qq -y \
    --allow-downgrades --allow-remove-essential --allow-change-held-packages \
    gcc at wget \
    espeak mpc mpg123 git ffmpeg spi-tools netcat \
    python3 python3-venv python3-dev python3-mutagen

USER ${USER}
ENV VIRTUAL_ENV=${INSTALLATION_PATH}/.venv
RUN python3 -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

WORKDIR ${HOME}
COPY --chown=${USER}:${USER} . ${INSTALLATION_PATH}/

RUN pip install --no-cache-dir -r ${INSTALLATION_PATH}/requirements.txt

ENV ZMQ_TMP_DIR libzmq
ENV ZMQ_VERSION 4.3.5
ENV ZMQ_PREFIX /usr/local

RUN [ "$(uname -m)" = "aarch64" ] && ARCH="arm64" || ARCH="$(uname -m)"; \
    wget https://github.com/pabera/libzmq/releases/download/v${ZMQ_VERSION}/libzmq5-${ARCH}-${ZMQ_VERSION}.tar.gz -O libzmq.tar.gz; \
    tar -xzf libzmq.tar.gz -C ${ZMQ_PREFIX}; \
    rm -f libzmq.tar.gz;

RUN export ZMQ_PREFIX=${PREFIX} && export ZMQ_DRAFT_API=1
RUN pip install -v --no-binary pyzmq --pre pyzmq

EXPOSE 5555 5556

WORKDIR ${INSTALLATION_PATH}/src/jukebox
