#!/usr/bin/env python3
import configparser
import os
import logging

from GPIODevices import *
import function_calls
from signal import pause
from RPi import GPIO
from config_compatibility import ConfigCompatibilityChecks


class gpio_control():

    def __init__(self, function_calls):
        self.devices = []
        self.function_calls = function_calls

        GPIO.setmode(GPIO.BCM)

        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel('INFO')
        self.logger.info('GPIO Started')

    def getFunctionCall(self, function_name):
        try:
            if function_name != 'None':
                return getattr(self.function_calls, function_name)
        except AttributeError:
            self.logger.error('Could not find FunctionCall {function_name}'.format(function_name=function_name))
        return lambda *args: None

    def generate_device(self, config, deviceName):
        print(deviceName)
        device_type = config.get('Type')
        if device_type == 'TwoButtonControl':
            self.logger.info('adding TwoButtonControl')
            return TwoButtonControl(
                config.getint('Pin1'),
                config.getint('Pin2'),
                self.getFunctionCall(config.get('functionCall1')),
                self.getFunctionCall(config.get('functionCall2')),
                functionCallTwoBtns=self.getFunctionCall(config.get('functionCallTwoButtons')),
                pull_up_down=config.get('pull_up_down', fallback='pull_up'),
                hold_mode=config.get('hold_mode', fallback=None),
                hold_time=config.getfloat('hold_time', fallback=0.3),
                bouncetime=config.getint('bouncetime', fallback=500),
                edge=config.get('edge', fallback='falling'),
                antibouncehack=config.getboolean('antibouncehack', fallback=False),
                name=deviceName)
        elif device_type in ('Button', 'SimpleButton'):
            return SimpleButton(config.getint('Pin'),
                                action=self.getFunctionCall(config.get('functionCall')),
                                action2=self.getFunctionCall(config.get('functionCall2', fallback='None')),
                                name=deviceName,
                                bouncetime=config.getint('bouncetime', fallback=500),
                                antibouncehack=config.getboolean('antibouncehack', fallback=False),
                                edge=config.get('edge', fallback='falling'),
                                hold_mode=config.get('hold_mode', fallback=None),
                                hold_time=config.getfloat('hold_time', fallback=0.3),
                                pull_up_down=config.get('pull_up_down', fallback='pull_up'))
        elif device_type == 'LED':
            return LED(config.getint('Pin'),
                                name=deviceName,
                                initial_value=config.getboolean('initial_value', fallback=True))
        elif device_type in ('StatusLED', 'MPDStatusLED'):
            return StatusLED(config.getint('Pin'), name=deviceName)
        elif device_type == 'RotaryEncoder':
            return RotaryEncoder(config.getint('Pin1'),
                    config.getint('Pin2'),
                    self.getFunctionCall(config.get('functionCall1')),
                    self.getFunctionCall(config.get('functionCall2')),
                    config.getfloat('timeBase', fallback=0.1),
                    name=deviceName)
        elif device_type == 'ShutdownButton':
            return ShutdownButton(pin=config.getint('Pin'),
                                  action=self.getFunctionCall(config.get('functionCall', fallback='functionCallShutdown')),
                                  name=deviceName,
                                  bouncetime=config.getint('bouncetime', fallback=500),
                                  antibouncehack=config.getboolean('antibouncehack', fallback=False),
                                  edge=config.get('edge', fallback='falling'),
                                  hold_time=config.getfloat('hold_time', fallback=3.0),
                                  iteration_time=config.getfloat('iteration_time', fallback=0.2),
                                  led_pin=config.getint('led_pin', fallback=None),
                                  pull_up_down=config.get('pull_up_down', fallback='pull_up'))
        self.logger.warning('cannot find {}'.format(deviceName))
        return None

    def get_all_devices(self, config):
        self.logger.info(config.sections())
        for section in config.sections():
            if config.getboolean(section, 'enabled', fallback=False):
                self.logger.info('adding GPIO-Device, {}'.format(section))
                device = self.generate_device(config[section], section)
                if device is not None:
                    self.devices.append(device)
                else:
                    self.logger.warning('Could not add Device {} with {}'.format(section, config.items(section)))
            else:
                self.logger.info('Device {} not enabled'.format(section))
        return self.devices

    # Sets the led value at the shutdown button that should be used in case of the shutdown
    # sequence is cancelled if StatusLED and ShutdownLED use the sampe GPIO
    def checkDevicesDependencies(self):
        shutdownButtonFound = statusLedFound = None
        for dev in self.devices:
            if isinstance(dev, ShutdownButton):
                shutdownButtonFound = dev
            elif isinstance(dev, StatusLED):
                statusLedFound = dev
        if statusLedFound and shutdownButtonFound:
            if statusLedFound.pin == shutdownButtonFound.led_pin:
                shutdownButtonFound.led_state_shutdown_cancelled = GPIO.HIGH

    def print_all_devices(self):
        for dev in self.devices:
            print(dev)

    def gpio_loop(self):
        self.logger.info('Ready for taking actions')
        try:
            pause()
        except KeyboardInterrupt:
            pass
        self.logger.info('Exiting GPIO Control')


if __name__ == "__main__":
    config = configparser.ConfigParser(inline_comment_prefixes=";", delimiters=(':', '='))
    config_path = os.path.expanduser('/home/pi/RPi-Jukebox-RFID/settings/gpio_settings.ini')
    config.read(config_path)
    
    ConfigCompatibilityChecks(config, config_path)

    phoniebox_function_calls = function_calls.phoniebox_function_calls()
    gpio_controler = gpio_control(phoniebox_function_calls)

    devices = gpio_controler.get_all_devices(config)
    gpio_controler.checkDevicesDependencies()
    gpio_controler.print_all_devices()
    gpio_controler.gpio_loop()
