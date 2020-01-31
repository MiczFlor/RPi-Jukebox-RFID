import configparser
import logging

import mock

from scripts.RotaryEncoder import RotaryEncoderClickable, getRotaryEncoderFunction
from scripts.helperscripts import function_calls
from scripts.helperscripts.function_calls import getFunctionCall
from scripts.rotary_encoder_base import RotaryEncoder

logger = logging.getLogger(__name__)


def functionCallTwoButtons(btn1, btn2, functionCall1, functionCall2, functionCallBothPressed=None):
    def functionCallTwoButtons():
        if btn1.is_pressed and btn2.is_pressed:
            logger.debug("Both buttons was pressed")
            if functionCallBothPressed is not None:
                return functionCallBothPressed()
            logger.debug('No two button pressed action defined')
        elif btn1.is_pressed:
            return functionCall1()
        elif btn2.is_pressed:
            return functionCall2()
        else:
            logger.error("Error: Could not analyse two button action")
            return None

    return functionCallTwoButtons


class TwoButtonControl:
    def __init__(self,
                 bcmPin1,
                 bcmPin2,
                 functionCallBtn1,
                 functionCallBtn2,
                 functionCallTwoBtns=None,
                 pull_up=True,
                 hold_repeat=True,
                 hold_time=0.3,
                 name='TwoButtonControl'):
        self.functionCallBtn1 = functionCallBtn1
        self.functionCallBtn2 = functionCallBtn2
        self.functionCallTwoBtns = functionCallTwoBtns
        self.bcmPin1 = bcmPin1
        self.bcmPin2 = bcmPin2
        self.btn1 = mock.Mock()  # Button(bcmPin1, pull_up=pull_up, hold_time=hold_time, hold_repeat=hold_repeat)

        self.btn2 = mock.Mock()  # Button(bcmPin2, pull_up=pull_up, hold_time=hold_time, hold_repeat=hold_repeat)
        generatedTwoButtonFunctionCall = functionCallTwoButtons(self.btn1,
                                                                self.btn2,
                                                                self.functionCallBtn1,
                                                                self.functionCallBtn2,
                                                                self.functionCallTwoBtns
                                                                )
        self.btn1.when_pressed = generatedTwoButtonFunctionCall
        self.btn2.when_pressed = generatedTwoButtonFunctionCall
        self.name = name

    def __repr__(self):
        two_btns_action = self.functionCallTwoBtns is not None
        return f'<TwoBtnControl-{self.name}({self.bcmPin1}, {self.bcmPin2},two_buttons_action={two_btns_action})>'


class VolumeControl:
    def __new__(self, config):
        if config.get('Type') == 'TwoButtonControl':
            return TwoButtonControl(
                config.getint('pinUp'),
                config.getint('pinDown'),
                getattr(function_calls,config.get('functionCallUp')),
                getattr(function_calls,config.get('functionCallDown')),
                functionCallTwoBtns=getattr(function_calls,config.get('functionCallTwoButtons')),
                pull_up=config.getboolean('pull_up', fallback=True),
                hold_repeat=config.getboolean('hold_repeat', fallback=True),
                hold_time=config.getfloat('hold_time', fallback=0.3),
                name='VolumeControl'
            )
        elif config.get('Type') == 'RotaryEncoder':
            return RotaryEncoder(
                config.getint('pinUp'),
                config.getint('pinDown'),
                getattr(function_calls,config.get('functionCallUp')),
                getattr(function_calls,config.get('functionCallDown')),
                config.getfloat('timeBase',fallback=0.1))
        elif config.get('Type') == 'RotaryEncoderClickable':
            encoder = RotaryEncoderClickable(
                pin_a = config.getint('pinUp'),
                pin_b = config.getint('pinDown'),
                button_pin = config.getint('pinClick'),
                encoder_pull_up =config.getboolean('pull_up', fallback=True),
                button_pull_up =config.getboolean('pull_up', fallback=True))
            encoder.when_rotated = getRotaryEncoderFunction(getattr(function_calls,config.get('functionCallUp')),
                getattr(function_calls,config.get('functionCallDown')),
                )
            encoder.when_pressed = getattr(function_calls, config.get('functionCallButton')),
            return encoder





def generate_device(config, deviceName):
    print(deviceName)
    if deviceName == 'VolumeControl':
        return VolumeControl(config[deviceName])


if __name__ == "__main__":
    config = configparser.ConfigParser()
    config.read('../settings/gpio_settings.ini')
    devices = []
    for section in config.sections():
        if config.get(section, 'enabled', fallback=False):
            devices.append(generate_device(config, section))
    for dev in devices:
        print(dev)
