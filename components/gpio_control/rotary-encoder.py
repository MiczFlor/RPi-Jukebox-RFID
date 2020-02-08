#!/usr/bin/python3
# rotary volume and track knob
# This script is compatible with any I2S DAC e.g. from Hifiberry, Justboom, ES9023, PCM5102A
# Please combine with corresponding gpio button script, which handles the button functionality of the encoder
# RPi-Jukebox-RFID/misc/sampleconfigs/gpio-buttons.py.rotaryencoder.sample

# these files belong all together:
# RPi-Jukebox-RFID/scripts/rotary-encoder.py
# RPi-Jukebox-RFID/scripts/RotaryEncoder.py
# RPi-Jukebox-RFID/misc/sampleconfigs/phoniebox-rotary-encoder.service.stretch-default.sample
# RPi-Jukebox-RFID/misc/sampleconfigs/gpio-buttons.py.rotaryencoder.sample
# See wiki for more info: https://github.com/MiczFlor/RPi-Jukebox-RFID/wiki

#
# circuit diagram for one of two possible encoders (volume), use GPIOs from code below for the tracks
# (capacitors are optionally)
# KY-040 is just one example, typically the pins are named A and B instead of Clock and Data
#
#       .---------------.                      .---------------.
#       |               |                      |               |
#       |        B / DT |------o---------------| GPIO 5        |
#       |               |      |               |               |
#       |       A / CLK |------)----o----------| GPIO 6        |
#       |               |      |    |          |               |
#       |           SW  |------)----)----------| GPIO 3        |
#       |               |      |    |          |               |
#       |           +   |------)----)----------| 3.3V          |
#       |               |      |    |          |               |
#       |           GND |------)----)----------| GND           |
#       |               |      |    |          |               |
#       '---------------'      |    |          '---------------'
#            KY-040            |    |              Raspberry
#                              |    |
#                             ---  ---
#                       100nF ---  --- 100nF
#                              |    |
#                              |    |
#                              |    |
#                             ===  ===
#                             GND  GND
#

import RPi.GPIO as GPIO
import sys
from signal import pause

from components.gpio_control.RotaryEncoder import RotaryEncoder

from scripts.helperscripts import function_calls

import logging
logger = logging.getLogger(__name__)

encVol = None
encTrack = None
useVolume = True
useTrack = False
APinVol = 6
BPinVol = 5

APinTrack = 23
BPinTrack = 22

GPIO.setmode(GPIO.BCM)

if __name__ == "__main__":
    logging.basicConfig(level='INFO')
    try:
        if useVolume:
            logger.info('Starting RotaryEncoder for VolumeControl')
            encVol = RotaryEncoder(APinVol,
                                   BPinVol,
                                   getattr(function_calls, 'functionCallVolU'),
                                   getattr(function_calls, 'functionCallVolD'),
                                   timeBase=0.2,
                                   name='VolumeControl')
            encVol.start()
        if useTrack:
            logger.info('Starting RotaryEncoder for TrackControl')
            encTrack = RotaryEncoder(APinTrack,
                                     BPinTrack,
                                     getattr(function_calls, 'functionCallPlayerNext'),
                                     getattr(function_calls, 'functionCallPlayerPrev'),
                                     timeBase=0.05,
                                     name='TrackControl')
            encTrack.start()
        pause()
    except KeyboardInterrupt:
        if encVol:
            encVol.stop()
        if encTrack:
            encTrack.stop()
        GPIO.cleanup()
        logger.info("\nExiting rotary encoder decoder\n")
        # exit the application

    sys.exit(0)
