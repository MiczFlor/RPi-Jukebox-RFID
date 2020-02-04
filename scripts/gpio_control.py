import configparser
import logging

from SimpleButton import SimpleButton
from TwoButtonControl import TwoButtonControl
from helperscripts import function_calls

from RotaryEncoder import RotaryEncoder

logger = logging.getLogger(__name__)

def getFunctionCall(function_name):
    try:
        if function_name != 'None':
            return getattr(function_calls, function_name)
    except AttributeError:
        logger.error('Could not find FunctionCall {function_name}'.format(function_name=function_name))
    return lambda *args: None


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
    device_type = config.get('Type')
    if deviceName.lower() == 'VolumeControl'.lower():
        return VolumeControl(config)
    elif device_type == 'TwoButtonControl':
        return TwoButtonControl(
            config.getint('Pin1'),
            config.getint('Pin2'),
            getFunctionCall(config.get('functionCall1')),
            getFunctionCall(config.get('functionCall2')),
            functionCallTwoBtns=getFunctionCall(config.get('functionCallTwoButtons')),
            pull_up=config.getboolean('pull_up',fallback=True),
            hold_repeat=config.getboolean('hold_repeat', False),
            hold_time=config.getfloat('hold_time',fallback=0.3),
            name=deviceName)
    elif device_type in ('Button', 'SimpleButton'):
        return SimpleButton(config.getint('Pin'),
                            action=getFunctionCall(config.get('functionCall')),
                            name=deviceName,
                            bouncetime=config.getint('bouncetime', fallback=500),
                            edge=config.get('edge',fallback='FALLING'),
                            hold_repeat=config.getboolean('hold_repeat', False),
                            hold_time=config.getfloat('hold_time',fallback=0.3))
    logger.warning('cannot find {}'.format(deviceName))
    return None


def get_all_devices(config):
    devices = []
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


if __name__ == "__main__":
    config = configparser.ConfigParser()
    config.read('../settings/gpio_settings_test.ini')
    get_all_devices(config)
