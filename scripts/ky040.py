#!/usr/bin/python3
# rotary volume knob
# these files belong all together:
# RPi-Jukebox-RFID/scripts/rotary-encoder.py
# RPi-Jukebox-RFID/scripts/ky040.py
# RPi-Jukebox-RFID/misc/sampleconfigs/phoniebox-rotary-encoder.service.stretch-default.sample
# See wiki for more info: https://github.com/MiczFlor/RPi-Jukebox-RFID/wiki

import RPi.GPIO as GPIO

class KY040:

    def __init__(self, arg_clockPin, arg_dataPin, arg_rotaryCallbackCW=None, arg_rotaryCallbackCCW=None, arg_rotaryBouncetime=100, arg_switchBouncetime=100):
        # persist values
        self.clockPin = arg_clockPin
        self.dataPin = arg_dataPin
        self.rotaryCallbackCW = arg_rotaryCallbackCW
        self.rotaryCallbackCCW = arg_rotaryCallbackCCW
        self.rotaryBouncetime = arg_rotaryBouncetime

        # setup pins
        GPIO.setup(self.clockPin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(self.dataPin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

    def start(self):
        GPIO.add_event_detect(self.clockPin, GPIO.FALLING, callback=self._clockCallback, bouncetime=self.rotaryBouncetime)

    def stop(self):
        GPIO.remove_event_detect(self.clockPin)

    def _clockCallback(self, pin):
        if GPIO.input(self.clockPin) == 0:
            data = GPIO.input(self.dataPin)
            if data == 1:
                self.rotaryCallbackCCW()
            else:
                self.rotaryCallbackCW()
