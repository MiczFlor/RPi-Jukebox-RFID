FROM debian:bullseye-slim

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
    espeak mpc mpg123 git ffmpeg spi-tools netcat alsa-tools \
    python3 python3-dev python3-pip python3-mutagen python3-gpiozero

COPY . ${INSTALLATION_PATH}

RUN pip3 install --no-cache-dir -r ${INSTALLATION_PATH}/requirements.txt
RUN pip3 install pyzmq

EXPOSE 5555 5556

# Run Jukebox
# CMD bash
CMD python3 ${INSTALLATION_PATH}/src/jukebox/run_jukebox.py
