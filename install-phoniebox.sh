#!/usr/bin/env bash

# Install Sample config
cp ./misc/sampleconfigs/startupsound.mp3.sample ./shared/startupsound.mp3
cp ./misc/sampleconfigs/shutdownsound.mp3.sample ./shared/shutdownsound.mp3

# Install Python dependencies
pip install --no-cache-dir -r ./Phoniebox/requirements.txt