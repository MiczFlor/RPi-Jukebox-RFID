#!/usr/bin/python3
# rotary volume and track knob
# This script is compatible with any I2S DAC e.g. from Hifiberry, Justboom, ES9023, PCM5102A
# Please combine with corresponding gpio button script, which handles the button functionality of the encoder
# RPi-Jukebox-RFID/misc/sampleconfigs/gpio-buttons.py.rotaryencoder.sample

# these files belong all together:
# RPi-Jukebox-RFID/scripts/rotary-encoder.py
# RPi-Jukebox-RFID/scripts/ky040.py
# RPi-Jukebox-RFID/misc/sampleconfigs/phoniebox-rotary-encoder.service.stretch-default.sample
# RPi-Jukebox-RFID/misc/sampleconfigs/gpio-buttons.py.rotaryencoder.sample
# See wiki for more info: https://github.com/MiczFlor/RPi-Jukebox-RFID/wiki

#
# circuit diagram for one of two possible encoders (volume), use GPIOs from code below for the tracks
# (capacitors are optionally)
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
from ky040 import KY040
import os, time, sys
from signal import pause
from subprocess import check_call


def rotaryChangeCWVol():
   check_call("./scripts/playout_controls.sh -c=volumeup", shell=True)

def rotaryChangeCCWVol():
   check_call("./scripts/playout_controls.sh -c=volumedown", shell=True)

def rotaryChangeCWTrack():
   check_call("./scripts/playout_controls.sh -c=playernext", shell=True)

def rotaryChangeCCWTrack():
   check_call("./scripts/playout_controls.sh -c=playerprev", shell=True)

CLOCKPINVol = 5 
DATAPINVol = 6

CLOCKPINTrack = 22
DATAPINTrack = 23

GPIO.setmode(GPIO.BCM)

if __name__ == "__main__":

	try:
		ky040Vol = KY040(CLOCKPINVol, DATAPINVol, rotaryChangeCWVol, rotaryChangeCCWVol, 100)
		ky040Track = KY040(CLOCKPINTrack, DATAPINTrack, rotaryChangeCWTrack, rotaryChangeCCWTrack, 500)

		ky040Vol.start()
		ky040Track.start()
		pause()
	except KeyboardInterrupt:
		ky040Vol.stop()
		ky040Track.stop()
		GPIO.cleanup()
		print("\nExiting rotary encoder decoder\n")
		# exit the application
		sys.exit(0)