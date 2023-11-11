FROM debian:bullseye-slim

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
    gcc at wget \
    espeak mpc mpg123 git ffmpeg spi-tools netcat \
    python3 python3-venv python3-dev python3-pip python3-mutagen python3-gpiozero

ENV VIRTUAL_ENV=/opt/venv
RUN python3 -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

USER ${USER}
WORKDIR ${HOME}
COPY --chown=${USER}:${USER} . ${INSTALLATION_PATH}/

RUN pip install --no-cache-dir -r ${INSTALLATION_PATH}/requirements.txt
RUN pip install pyzmq

EXPOSE 5555 5556

WORKDIR ${INSTALLATION_PATH}/src/jukebox
