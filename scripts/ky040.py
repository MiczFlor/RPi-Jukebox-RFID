#!/usr/bin/python3
# rotary volume knob
# these files belong all together:
# RPi-Jukebox-RFID/scripts/rotary-encoder.py
# RPi-Jukebox-RFID/scripts/ky040.py
# RPi-Jukebox-RFID/misc/sampleconfigs/phoniebox-rotary-encoder.service.stretch-default.sample
# See wiki for more info: https://github.com/MiczFlor/RPi-Jukebox-RFID/wiki

import RPi.GPIO as GPIO

class KY040:

    def __init__(self, arg_clockPin, arg_dataPin, arg_switchPin=None, arg_rotaryCallbackCW=None, arg_rotaryCallbackCCW=None, arg_switchCallback=None, arg_rotaryBouncetime=100, arg_switchBouncetime=200):
        # persist values
        self.clockPin = arg_clockPin
        self.dataPin = arg_dataPin
        self.switchPin = arg_switchPin
        self.rotaryCallbackCW = arg_rotaryCallbackCW
        self.rotaryCallbackCCW = arg_rotaryCallbackCCW
        self.switchCallback = arg_switchCallback
        self.rotaryBouncetime = arg_rotaryBouncetime
        self.switchBouncetime = arg_switchBouncetime

        # setup pins
        # data and clock have pullups at the PCB
        GPIO.setup(self.clockPin, GPIO.IN)
        GPIO.setup(self.dataPin, GPIO.IN)

        if None != self.switchPin:
            GPIO.setup(self.switchPin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

    def start(self):
        GPIO.add_event_detect(self.clockPin, GPIO.FALLING, callback=self._clockCallback, bouncetime=self.rotaryBouncetime)

        if None != self.switchPin:
            GPIO.add_event_detect(self.switchPin, GPIO.FALLING, callback=self._switchCallback, bouncetime=self.switchBouncetime)

    def stop(self):
        GPIO.remove_event_detect(self.clockPin)

        if None != self.switchPin:
            GPIO.remove_event_detect(self.switchPin)

    def _clockCallback(self, pin):
        if GPIO.input(self.clockPin) == 0:
            data = GPIO.input(self.dataPin)
            if data == 1:
                self.rotaryCallbackCCW()
            else:
                self.rotaryCallbackCW()

    def _switchCallback(self, pin):
        if None == self.switchPin:
            return

        if GPIO.input(self.switchPin) == 0:
            self.switchCallback()

