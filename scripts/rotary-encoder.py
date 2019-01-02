#!/usr/bin/python3
# rotary volume and track knob
# This script is compatible with any I2S DAC e.g. from Hifiberry, Justboom, ES9023, PCM5102A
# Please combine with corresponding gpio button script, which handles the button functionality of the encoder
# RPi-Jukebox-RFID/misc/sampleconfigs/gpio-buttons.py.rotaryencoder.sample

# these files belong all together:
# RPi-Jukebox-RFID/scripts/rotary-encoder.py
# RPi-Jukebox-RFID/scripts/rotary_encoder_base.py
# RPi-Jukebox-RFID/misc/sampleconfigs/phoniebox-rotary-encoder.service.stretch-default.sample
# RPi-Jukebox-RFID/misc/sampleconfigs/gpio-buttons.py.rotaryencoder.sample
# See wiki for more info: https://github.com/MiczFlor/RPi-Jukebox-RFID/wiki

#
# circuit diagram for one of two possible encoders (volume), use GPIOs from code below for the tracks
# (capacitors are optionally)
# KY-040 is just one example, typically the pins are named A nd B instead of Clock and Data
#
#       .---------------.                      .---------------.
#       |               |                      |               |
#       |           CLK |------o---------------| GPIO 5        |
#       |               |      |               |               |
#       |           DT  |------)----o----------| GPIO 6        |
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
from rotary_encoder_base import RotaryEncoder as enc
import os, time, sys
from signal import pause
from subprocess import check_call


def rotaryChangeCWVol(steps):
   check_call("./scripts/playout_controls.sh -c=volumeup -v="+str(steps), shell=True)

def rotaryChangeCCWVol(steps):
   check_call("./scripts/playout_controls.sh -c=volumedown -v="+str(steps), shell=True)

def rotaryChangeCWTrack(steps):
   check_call("./scripts/playout_controls.sh -c=playernext", shell=True)

def rotaryChangeCCWTrack(steps):
   check_call("./scripts/playout_controls.sh -c=playerprev", shell=True)

APinVol = 5 
BPinVol = 6

APinTrack = 22
BPinTrack = 23

GPIO.setmode(GPIO.BCM)

if __name__ == "__main__":

	try:
		encVol = enc(APinVol, BPinVol, rotaryChangeCWVol, rotaryChangeCCWVol, 0.2)
		encTrack = enc(APinTrack, BPinTrack, rotaryChangeCWTrack, rotaryChangeCCWTrack, 0.05)

		encVol.start()
		encTrack.start()
		pause()
	except KeyboardInterrupt:
		encVol.stop()
		encTrack.stop()
		GPIO.cleanup()
		print("\nExiting rotary encoder decoder\n")
		# exit the application
		sys.exit(0)