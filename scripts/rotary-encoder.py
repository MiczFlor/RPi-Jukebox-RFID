#!/usr/bin/python3
# rotary volume knob
# these files belong all together:
# RPi-Jukebox-RFID/scripts/rotary-encoder.py
# RPi-Jukebox-RFID/scripts/ky040.py
# RPi-Jukebox-RFID/misc/sampleconfigs/phoniebox-rotary-encoder.service.stretch-default.sample
# See wiki for more info: https://github.com/MiczFlor/RPi-Jukebox-RFID/wiki

#
# circuit diagram
# (capacitors are optionally)
#
#       .---------------.                      .---------------.
#       |               |                      |               |
#       |           CLK |------o---------------| GPIO 5        |
#       |               |      |               |               |
#       |           DT  |------)----o----------| GPIO 6        |
#       |               |      |    |          |               |
#       |           SW  |------)----)----------| GPIO 13       |
#       |               |      |    |          |               |
#       |           +   |------)----)----------| 5V            |
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
import os, time
from subprocess import check_call


def rotaryChangeCWVol():
   check_call("./scripts/playout_controls.sh -c=volumeup", shell=True)

def rotaryChangeCCWVol():
   check_call("./scripts/playout_controls.sh -c=volumedown", shell=True)

def rotaryChangeCWTrack():
   check_call("./scripts/playout_controls.sh -c=playernext", shell=True)

def rotaryChangeCCWTrack():
   check_call("./scripts/playout_controls.sh -c=playerprev", shell=True)


if __name__ == "__main__":

   CLOCKPINVol = 27 
   DATAPINVol = 17

   CLOCKPINTrack = 22
   DATAPINTrack = 23

   GPIO.setmode(GPIO.BCM)

   ky040Vol = KY040(CLOCKPINVol, DATAPINVol, rotaryChangeCWVol, rotaryChangeCCWVol)

   ky040Track = KY040(CLOCKPINTrack, DATAPINTrack, rotaryChangeCWTrack, rotaryChangeCCWTrack)

   ky040Vol.start()
   ky040Track.start()

   try:
      while True:
         time.sleep(0.2)
   finally:
      ky040Vol.stop()
      ky040Track.stop()
      GPIO.cleanup()






