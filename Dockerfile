FROM debian:buster

# Prepare Raspberry Pi like environment

# These are only dependencies that are required to get as close to the
# Raspberry Pi environment as possible. They don't include Phoniebox
# specific dependencies. They will be installed in a separate install script
RUN apt-get update && apt-get install -y \
    alsa-utils \
    libasound2-dev \
    libasound2-plugins \
    pulseaudio \
    pulseaudio-utils \
    --no-install-recommends \
    && rm -rf /var/lib/apt/lists/*
 
RUN cd /home && mkdir pi
ENV HOME /home/pi/RPi-Jukebox-RFID
ENV DEV_FOLDER ${HOME}/docker-development

RUN useradd --create-home --home-dir $HOME pi \
    && usermod -aG audio,pulse,pulse-access pi \
    && chown -R pi:pi $HOME

WORKDIR $HOME

# Phoniebox
# Install all Phoniebox dependencies
RUN apt-get update && apt-get install -qq -y \
    --allow-downgrades --allow-remove-essential --allow-change-held-packages \
    gcc lighttpd php7.3-common php7.3-cgi php7.3 php-zmq at \
    mpd mpc mpg123 git ffmpeg spi-tools netcat alsa-tools \
    python3 python3-dev python3-pip python3-mutagen python3-gpiozero
#samba samba-common-bin
#raspberrypi-kernel-headers
#resolvconf
#python3-spidev

RUN update-alternatives --install /usr/bin/python python /usr/bin/python3.7 1

COPY . .

# Install Phoniebox
RUN chmod +x ${DEV_FOLDER}/install-phoniebox.sh ${DEV_FOLDER}/start-phoniebox.sh
RUN ${DEV_FOLDER}/install-phoniebox.sh

# Run Phoniebox
CMD ${DEV_FOLDER}/start-phoniebox.sh && bash
