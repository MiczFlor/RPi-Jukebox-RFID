#!/usr/bin/python3
# rotary volume knob
# these files belong all together:
# RPi-Jukebox-RFID/scripts/rotary-encoder.py
# RPi-Jukebox-RFID/scripts/rotary_encoder_base.py
# RPi-Jukebox-RFID/misc/sampleconfigs/phoniebox-rotary-encoder.service.stretch-default.sample
# See wiki for more info: https://github.com/MiczFlor/RPi-Jukebox-RFID/wiki

import RPi.GPIO as GPIO
from timeit import default_timer as timer
import ctypes

c_uint8 = ctypes.c_uint8

class Flags_bits( ctypes.LittleEndianStructure ):
     _fields_ = [
                 ("A", c_uint8, 1 ),  # asByte & 1
                 ("B", c_uint8, 1 ),  # asByte & 2
                ]
 
class Flags( ctypes.Union ):
     _anonymous_ = ("bit",)
     _fields_ = [
                 ("bit",    Flags_bits ),
                 ("asByte", c_uint8    )
                ]

class RotaryEncoder:

    # select Enocder state bits
    KeyIncr = 0b00000010
    KeyDecr = 0b00000001

    tblEncoder = [
        0b00000011, 0b00000111, 0b00010011, 0b00000011,
        0b00001011, 0b00000111, 0b00000011, 0b00000011,
        0b00001011, 0b00000111, 0b00001111, 0b00000011,
        0b00001011, 0b00000011, 0b00001111, 0b00000001,
        0b00010111, 0b00000011, 0b00010011, 0b00000011,
        0b00010111, 0b00011011, 0b00010011, 0b00000011,
        0b00010111, 0b00011011, 0b00000011, 0b00000010]

    def __init__(self, arg_Apin, arg_Bpin, arg_rotaryCallbackCW=None, arg_rotaryCallbackCCW=None, arg_TimeBase=0.1):
        # persist values
        self.Apin = arg_Apin
        self.Bpin = arg_Bpin
        self.rotaryCallbackCW = arg_rotaryCallbackCW
        self.rotaryCallbackCCW = arg_rotaryCallbackCCW
        self.TimeBase = arg_TimeBase

        self.EncoderState = Flags()	# stores the encoder state machine state
        self.StartTime = timer()

        # setup pins
        GPIO.setup(self.Apin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(self.Bpin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

    def start(self):
        GPIO.add_event_detect(self.Apin, GPIO.BOTH, callback=self._Callback)
        GPIO.add_event_detect(self.Bpin, GPIO.BOTH, callback=self._Callback)

    def stop(self):
        GPIO.remove_event_detect(self.Apin)
        GPIO.remove_event_detect(self.Bpin)

    def _StepSize(self):
        end = timer()
        duration = end - self.StartTime
        self.StartTime = end
        return int(self.TimeBase/duration) + 1

    def _Callback(self, pin):
        # construct new state machine input from encoder state and old state
        self.EncoderState.A = GPIO.input(self.Apin)
        self.EncoderState.B = GPIO.input(self.Bpin)
        self.EncoderState.asByte = self.tblEncoder[self.EncoderState.asByte]

        if self.KeyIncr == self.EncoderState.asByte:
            self.rotaryCallbackCW(self._StepSize())

        elif self.KeyDecr == self.EncoderState.asByte:
            self.rotaryCallbackCCW(self._StepSize())
