FROM python:3.9-buster

RUN apt-get update && apt-get install -y \
    alsa-utils \
    libasound2-dev \
    libasound2-plugins \
    pulseaudio \
    pulseaudio-utils \
    --no-install-recommends \
    && rm -rf /var/lib/apt/lists/*
 
ENV HOME /home/phoniebox-daemon

RUN useradd --create-home --home-dir $HOME phoniebox-daemon \
    && usermod -aG audio,pulse,pulse-access phoniebox-daemon \
    && chown -R phoniebox-daemon:phoniebox-daemon $HOME

WORKDIR $HOME

COPY ./Phoniebox/requirements.txt ./Phoniebox/

RUN pip install --no-cache-dir -r ./Phoniebox/requirements.txt

COPY . .

CMD [ "python", "./Phoniebox/PhonieboxDaemon.py" ]
