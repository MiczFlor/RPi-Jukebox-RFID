#!/usr/bin/env python3
import configparser
import os
import logging

from GPIODevices import *
import function_calls
from signal import pause

from RPi import GPIO

# from GPIODevices.VolumeControl import VolumeControl
# from GPIODevices.led import LED, MPDStatusLED

GPIO.setmode(GPIO.BCM)

logger = logging.getLogger(__name__)


def getFunctionCall(function_name):
    try:
        if function_name != 'None':
            return getattr(function_calls, function_name)
    except AttributeError:
        logger.error('Could not find FunctionCall {function_name}'.format(function_name=function_name))
    return lambda *args: None


def generate_device(config, deviceName):
    print(deviceName)
    device_type = config.get('Type')
    if deviceName.lower() == 'VolumeControl'.lower():
        return VolumeControl(config)
    elif device_type == 'TwoButtonControl':
        logger.info('adding TwoButtonControl')
        return TwoButtonControl(
            config.getint('Pin1'),
            config.getint('Pin2'),
            getFunctionCall(config.get('functionCall1')),
            getFunctionCall(config.get('functionCall2')),
            functionCallTwoBtns=getFunctionCall(config.get('functionCallTwoButtons')),
            pull_up=config.getboolean('pull_up', fallback=True),
            hold_repeat=config.getboolean('hold_repeat', False),
            hold_time=config.getfloat('hold_time', fallback=0.3),
            name=deviceName)
    elif device_type in ('Button', 'SimpleButton'):
        return SimpleButton(config.getint('Pin'),
                            action=getFunctionCall(config.get('functionCall')),
                            name=deviceName,
                            bouncetime=config.getint('bouncetime', fallback=500),
                            edge=config.get('edge', fallback='FALLING'),
                            hold_repeat=config.getboolean('hold_repeat', False),
                            hold_time=config.getfloat('hold_time', fallback=0.3),
                            pull_up_down=config.get('pull_up_down', fallback=GPIO.PUD_UP))
    elif device_type == 'LED':
        return LED(config.getint('Pin'),
                            name=deviceName,
                            initial_value=config.getboolean('initial_value', fallback=True))
    elif device_type == 'MPDStatusLED':
        return MPDStatusLED(config.getint('Pin'),
                            host=config.get('host', fallback='localhost'),
                            port=config.getint('port', fallback=6600),
                            name=deviceName
                            )
    elif device_type == 'RotaryEncoder':
        return RotaryEncoder(config.getint('pinUp'),
                config.getint('pinDown'),
                getFunctionCall(config.get('functionCallUp')),
                getFunctionCall(config.get('functionCallDown')),
                config.getfloat('timeBase', fallback=0.1),
                name=deviceName)
    elif device_type == 'ShutdownButton':
        return ShutdownButton(pin=config.getint('Pin'),
                              action=getFunctionCall(config.get('functionCall',fallback='functionCallShutdown')),
                              name=deviceName,
                              bouncetime=config.getint('bouncetime', fallback=500),
                              edge=config.get('edge', fallback='FALLING'),
                              hold_repeat=config.getboolean('hold_repeat', False),
                              hold_time=config.getfloat('hold_time', fallback=0.3),
                              pull_up_down=config.get('pull_up_down', fallback=GPIO.PUD_UP))
    logger.warning('cannot find {}'.format(deviceName))
    return None


def get_all_devices(config):
    devices = []
    logger.info(config.sections())
    for section in config.sections():
        if config.getboolean(section, 'enabled', fallback=False):
            logger.info('adding GPIO-Device, {}'.format(section))
            device = generate_device(config[section], section)
            if device is not None:
                devices.append(device)
            else:
                logger.warning('Could not add Device {} with {}'.format(section, config.items(section)))
        else:
            logger.info('Device {} not enabled'.format(section))
    for dev in devices:
        print(dev)
    return devices


if __name__ == "__main__":

    logging.basicConfig(level='INFO')
    logger = logging.getLogger()
    logger.setLevel('INFO')

    config = configparser.ConfigParser(inline_comment_prefixes=";")
    config_path = os.path.expanduser('/home/pi/RPi-Jukebox-RFID/settings/gpio_settings.ini')
    config.read(config_path)

    devices = get_all_devices(config)
    print(devices)
    logger.info('Ready for taking actions')
    try:
        pause()
    except KeyboardInterrupt:
        pass
    logger.info('Exiting GPIO Control')
