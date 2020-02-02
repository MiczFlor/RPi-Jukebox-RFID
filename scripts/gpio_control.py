import configparser
import logging

from scripts.helperscripts import function_calls
from scripts.helperscripts.function_calls import
from scripts.RotaryEncoder import RotaryEncoder

logger = logging.getLogger(__name__)

def getFunctionCall(function_name):
    return getattr(function_calls, function_name)


def functionCallTwoButtons(btn1, btn2, functionCall1, functionCallBothPressed=None):
    def functionCallTwoButtons(args):
        if btn1.is_pressed and btn2.is_pressed:
            logger.debug("Both buttons was pressed")
            if functionCallBothPressed is not None:
                logger.debug("Both Btns are pressed, action: functionCallBothPressed")
                return functionCallBothPressed(*args)
            logger.debug('No two button pressed action defined')
        elif btn1.is_pressed:
            logger.debug("Main Btn is pressed, secondary Btn not pressed, action: functionCall1")
            return functionCall1(*args)
        elif btn2.is_pressed:
            logger.debug("Main Btn is not pressed, action: no action")
        else:
            logger.error("Error: Could not analyse two button action")
            return None

    return functionCallTwoButtons

def parse_edge_key(edge):
        if edge in [GPIO.FALLING, GPIO.RAISING, GPIO.BOTH]:
            edge
        elif edge.lower() == 'falling':
            edge = GPIO.FALLING
        elif edge.lower() == 'raising':
            edge = GPIO.RAISING
        elif edge.lower() == 'both':
            edge = GPIO.BOTH
        else:
            raise KeyError('Unknown Edge type {edge}'.format(edge=edge))
        return edge


class Button:
    def __init__(self, pin, callbackFunction=lambda *args: None, name=None, bouncetime = 500, edge=GPIO.FALLING):
        edge = parse_edge_key(edge)

        self.pin = pin
        self.name = name
        self.bouncetime = bouncetime
        GPIO.setup(self.pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        self.callbackFunction = callbackFunction
        GPIO.add_event_detect(channel=self.pin, edge=edge, callback=self.callbackFunction, bouncetime=self.bouncetime)

    def __del__(self):
        GPIO.remove_event_detect(self.pin)

    @property
    def is_pressed(self):
        return GPIO.input(self.pin)

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
        self.btn1 = Button(
            pin=bcmPin1, callbackFunction=lambda *args: None, name=None, bouncetime=500, edge=GPIO.FALLING
            bcmPin1, pull_up=pull_up, hold_time=hold_time, hold_repeat=hold_repeat)

        self.btn2 = Button(bcmPin2, pull_up=pull_up, hold_time=hold_time, hold_repeat=hold_repeat)
        generatedTwoButtonFunctionCallBtn1 = functionCallTwoButtons(self.btn1,
                                                                self.btn2,
                                                                self.functionCallBtn1,
                                                                self.functionCallTwoBtns
                                                                )
        generatedTwoButtonFunctionCallBtn2 = self.functionCallBtn2

        self.btn1.when_pressed = generatedTwoButtonFunctionCallBtn1
        self.btn2.when_pressed = generatedTwoButtonFunctionCallBtn2
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


if __name__ == "__main__":
    config = configparser.ConfigParser()
    config.read('../settings/gpio_settings.ini')
    devices = []
    for section in config.sections():
        if config.get(section, 'enabled', fallback=False):
            devices.append(generate_device(config, section))
    for dev in devices:
        print(dev)
