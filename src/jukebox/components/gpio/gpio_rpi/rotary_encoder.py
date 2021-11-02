#!/usr/bin/env python3
# the basic function for the rotary encoder has been derived from
# https://github.com/bobrathbone/pirotary/blob/master/rotary_class.py

import RPi.GPIO as GPIO
import logging
import jukebox.utils as utils

logger = logging.getLogger('jb.gpio')


class RotaryEncoder:
    position = 0
    old_position = 0
    last_state = 0

    def __init__(self, name, config):
        self._logger = logger

        self.name = name
        self.pins = config.get('Pins')
        self.functionCW = config.get('FunctionCW')
        self.functionCCW = config.get('FunctionCCW')
        self.pinA = self.pins[0]
        self.pinB = self.pins[1]

        self._logger.debug(f'Initialize {name} RotaryEncoder({self.pinA}, {self.pinB})')
        self.timeBase = config.get('timeBase', default=0.1)

        self.action_after_increments = config.get('action_after_increments', default=2)

        # setup pins
        GPIO.setup(self.pinA, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(self.pinB, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        self._is_active = False
        self.start()

    def start(self):
        self._logger.debug(f'Start Event Detection for: {self.name} ({self.pinA},{self.pinB}')
        self._is_active = True
        GPIO.add_event_detect(self.pinA, GPIO.BOTH, callback=self._Callback)
        GPIO.add_event_detect(self.pinB, GPIO.BOTH, callback=self._Callback)

    def stop(self):
        self._logger.debug(f'Stop Event Detection for: {self.name} ({self.pinA},{self.pinB}')
        GPIO.remove_event_detect(self.pinA)
        GPIO.remove_event_detect(self.pinB)
        self._is_active = False

    def __del__(self):
        if self.is_active:
            self.stop()

    @property
    def is_active(self):
        return self._is_active

    def _Callback(self, pin):
        statusA = GPIO.input(self.pinA)
        statusB = GPIO.input(self.pinB)

        statusC = statusA ^ statusB
        new_state = statusA * 4 + statusB * 2 + statusC * 1
        delta = (new_state - self.last_state) % 4
        self.last_state = new_state

        if delta == 1:
            self.position += 1
        elif delta == 3:
            self.position -= 1

        delta_pos = self.position - self.old_position

        if delta_pos >= self.action_after_increments:
            self._logger.debug(f'{self.name} @ {self.position}: Calling functionCW {self.functionCW}')
            utils.decode_and_call_rpc_command(self.functionCW, self._logger)
            self.old_position = self.position
        if delta_pos <= -self.action_after_increments:
            self._logger.debug(f'{self.name} @ {self.position}: Calling functionCCW {self.functionCW}')
            utils.decode_and_call_rpc_command(self.functionCCW, self._logger)
            self.old_position = self.position
