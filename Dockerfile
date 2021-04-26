FROM python:3.9-buster

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
 
ENV HOME /home/phoniebox

RUN useradd --create-home --home-dir $HOME phoniebox \
    && usermod -aG audio,pulse,pulse-access phoniebox \
    && chown -R phoniebox:phoniebox $HOME

WORKDIR $HOME

# Phoniebox
COPY . .

# Install Phoniebox
RUN ["chmod", "+x", "./install-phoniebox.sh"]
RUN ./install-phoniebox.sh

# Run Phoniebox
CMD [ "python", "./Phoniebox/PhonieboxDaemon.py" ]
