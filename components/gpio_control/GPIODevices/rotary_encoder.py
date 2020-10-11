#!/usr/bin/env python3
# rotary volume knob
# these files belong all together:
# RPi-Jukebox-RFID/scripts/rotary-encoder.py
# RPi-Jukebox-RFID/scripts/rotary_encoder.py
# RPi-Jukebox-RFID/misc/sampleconfigs/phoniebox-rotary-encoder.service.stretch-default.sample
# See wiki for more info: https://github.com/chbuehlmann/RPi-Jukebox-RFID/wiki

import RPi.GPIO as GPIO
from timeit import default_timer as timer
import ctypes
import logging
from signal import pause

logger = logging.getLogger(__name__)

c_uint8 = ctypes.c_uint8


class Flags_bits(ctypes.LittleEndianStructure):
    _fields_ = [
        ("A", c_uint8, 1),  # asByte & 1
        ("B", c_uint8, 1),  # asByte & 2
    ]


class Flags(ctypes.Union):
    _anonymous_ = ("bit",)
    _fields_ = [
        ("bit", Flags_bits),
        ("asByte", c_uint8)
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

    def __init__(self, pinA, pinB, functionCallIncr=None, functionCallDecr=None, timeBase=0.1,
                 name='RotaryEncoder'):
        logger.debug('Initialize {name} RotaryEncoder({arg_Apin}, {arg_Bpin})'.format(
            arg_Apin=pinA,
            arg_Bpin=pinB,
            name=name if name is not None else ''
        ))
        self.name = name
        # persist values
        self.pinA = pinA
        self.pinB = pinB
        self.functionCallbackIncr = functionCallIncr
        self.functionCallbackDecr = functionCallDecr
        self.timeBase = timeBase

        self.encoderState = Flags()  # stores the encoder state machine state
        self.startTime = timer()

        # setup pins
        GPIO.setup(self.pinA, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(self.pinB, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        self._is_active = False
        self.start()

    def __repr__(self):
        repr_str = '<{class_name}{object_name} on pin_a {pin_a},' + \
                   ' pin_b {pin_b},timBase {time_base} is_active={is_active}%s>'
        return repr_str.format(
            class_name=self.__class__.__name__,
            object_name=':{}'.format(self.name) if self.name is not None else '',
            pin_a=self.pinA,
            pin_b=self.pinB,
            time_base=self.timeBase,
            is_active=self.is_active)

    def start(self):
        logger.debug('Start Event Detection on {} and {}'.format(self.pinA, self.pinB))
        self._is_active = True
        GPIO.add_event_detect(self.pinA, GPIO.BOTH, callback=self._Callback)
        GPIO.add_event_detect(self.pinB, GPIO.BOTH, callback=self._Callback)

    def stop(self):
        logger.debug('Stop Event Detection on {} and {}'.format(self.pinA, self.pinB))
        GPIO.remove_event_detect(self.pinA)
        GPIO.remove_event_detect(self.pinB)
        self._is_active = False

    def __del__(self):
        if self.is_active:
            self.stop()

    @property
    def is_active(self):
        return self._is_active

    def _StepSize(self):
        end = timer()
        duration = end - self.startTime
        self.startTime = end
        return int(self.timeBase / duration) + 1

    def _Callback(self, pin):
        logger.debug('EventDetection Called')
        # construct new state machine input from encoder state and old state
        statusA = GPIO.input(self.pinA)
        statusB = GPIO.input(self.pinB)

        self.encoderState.A = statusA
        self.encoderState.B = statusB
        logger.debug('new encoderState: "{}" -> {}, {},{}'.format(
            self.encoderState.asByte,
            self.tblEncoder[self.encoderState.asByte], statusA, statusB
        ))
        current_state = self.encoderState.asByte
        self.encoderState.asByte = self.tblEncoder[current_state]

        if self.KeyIncr == self.encoderState.asByte:
            steps = self._StepSize()
            logger.info('{name}: Calling functionIncr {steps}'.format(
                name=self.name, steps=steps))
            self.functionCallbackIncr(steps)
        elif self.KeyDecr == self.encoderState.asByte:
            steps = self._StepSize()
            logger.info('{name}: Calling functionDecr {steps}'.format(
                name=self.name, steps=steps))
            self.functionCallbackDecr(steps)
        else:
            logger.debug('Ignoring encoderState: "{}"'.format(self.encoderState.asByte))


if __name__ == "__main__":
    logging.basicConfig(level='INFO')
    GPIO.setmode(GPIO.BCM)
    pin1 = int(input('please enter first pin'))
    pin2 = int(input('please enter second pin'))
    func1 = lambda *args: print('Function Incr executed with {}'.format(args))
    func2 = lambda *args: print('Function Decr executed with {}'.format(args))
    rotarty_encoder = RotaryEncoder(pin1, pin2, func1, func2)

    print('running')
    pause()
