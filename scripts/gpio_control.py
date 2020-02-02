import configparser
import logging
from TwoButtonControl import TwoButtonControl
from helperscripts import function_calls

from RotaryEncoder import RotaryEncoder

logger = logging.getLogger(__name__)

def getFunctionCall(function_name):
    return getattr(function_calls, function_name)


class VolumeControl:
    def __new__(self, config):
        if config.get('Type') == 'TwoButtonControl':
            return TwoButtonControl(
                config.getint('pinUp'),
                config.getint('pinDown'),
                getFunctionCall(config.get('functionCallUp')),
                getFunctionCall(config.get('functionCallDown')),
                functionCallTwoBtns=getFunctionCall(config.get('functionCallTwoButtons')),
                pull_up=config.getboolean('pull_up', fallback=True),
                hold_repeat=config.getboolean('hold_repeat', fallback=True),
                hold_time=config.getfloat('hold_time', fallback=0.3),
                name='VolumeControl'
            )
        elif config.get('Type') == 'RotaryEncoder':
            return RotaryEncoder(
                config.getint('pinUp'),
                config.getint('pinDown'),
                getFunctionCall(config.get('functionCallUp')),
                getFunctionCall(config.get('functionCallDown')),
                config.getfloat('timeBase',fallback=0.1),
                name='RotaryVolumeControl')






def generate_device(config, deviceName):
    print(deviceName)
    if deviceName == 'VolumeControl':
        return VolumeControl(config[deviceName])
    else:

        print('cannot find {}'.format(deviceName))


def get_all_devices(config):
    devices = []
    for section in config.sections():
        if config.get(section, 'enabled', fallback=False):
            logger.info('adding GPIO-Device, {}'.format(section))
            devices.append(generate_device(config, section))
    for dev in devices:
        print(dev)


if __name__ == "__main__":
    config = configparser.ConfigParser()
    config.read('../settings/gpio_settings.ini')
    get_all_devices(config)
