try:
    from simple_button import SimpleButton
except ImportError:
    from .simple_button import SimpleButton
from subprocess import check_call
from RPi import GPIO

import os
from pathlib import Path
import logging
logger = logging.getLogger(__name__)

GPIO.setmode(GPIO.BCM)


class TwoButtonLumaOledControl:
    MODE_NORMAL = 0
    MODE_CONTRAST = 1
    MODE_SPECIAL_INFO = 2
    SPECIALMARKER = "/tmp/o4p_overview.temp"
    OLEDCONFIG = "/home/pi/oled_phoniebox/oled_phoniebox.conf"

    def __init__(
        self, bcmPin1, bcmPin2, functionCallBtn1, functionCallBtn2, pull_up=True, hold_repeat=True, hold_time=0.3,
        name='TwoButtonOledControl'
    ):
        self.name = name
        self.bcmPin1 = bcmPin1
        self.bcmPin2 = bcmPin2
        self.functionCall1 = functionCallBtn1
        self.functionCall2 = functionCallBtn2

        self.btn1 = SimpleButton(
            name=name + 'Btn1',
            pin=bcmPin1,
            action=self.callbackHandler,
            edge=GPIO.FALLING,
            bouncetime=500,
            hold_time=hold_time,
            hold_repeat=hold_repeat
        )
        self.btn1.callback_with_pin_argument = True

        self.btn2 = SimpleButton(
            name=name + 'Btn2',
            pin=bcmPin2,
            action=self.callbackHandler,
            edge=GPIO.FALLING,
            bouncetime=500,
            hold_time=hold_time,
            hold_repeat=hold_repeat
        )
        self.btn2.callback_with_pin_argument = True

        self.mode = self.MODE_NORMAL

    def callbackHandler(self, *args):
        if self.btn1.is_pressed and self.btn2.is_pressed:
            self.cycleMode()
            return

        if self.mode == self.MODE_NORMAL:
            self.callRegularFunction(*args)
        else:
            self.callContrastFunction(*args)

    def cycleMode(self):
        if self.mode == self.MODE_NORMAL:
            self.mode = self.MODE_CONTRAST
        elif self.mode == self.MODE_CONTRAST:
            self.mode = self.MODE_SPECIAL_INFO
            self.showSpecialInfo()
        else:
            self.hideSpecialInfo()
            self.mode = self.MODE_NORMAL

    def callRegularFunction(self, *args):
        if self.btn1.is_pressed:
            self.functionCall1(*args)
        elif self.btn2.is_pressed:
            self.functionCall2(*args)
        else:
            logger.warn("callRegularFunction called but no button was pressed")

    def callContrastFunction(self, *args):
        if self.btn1.is_pressed:
            self.contrastDown()
        elif self.btn2.is_pressed:
            self.contrastUp()
        else:
            logger.warn("callSpecialFunction called but no button was pressed")

    def getOledConfig(self):
        import configparser
        config = configparser.ConfigParser()
        config.read(self.OLEDCONFIG)
        config.sections()
        return config

    def contrastUp(self):
        self.changeContrast(+85)

    def contrastDown(self):
        self.changeContrast(-85)

    def changeContrast(self, delta):
        oledConfig = self.getOledConfig()
        currcontrast = int(oledConfig['GENERAL']['contrast'])
        newContrast = currcontrast + delta
        if 0<= newContrast <= 255 and currcontrast != "":
            oledConfig.set('GENERAL', 'contrast', str(newContrast))
            with open(self.OLEDCONFIG, 'w') as configfile:
                oledConfig.write(configfile)

    def showSpecialInfo(self):
        Path(self.SPECIALMARKER).touch()

    def hideSpecialInfo(self):
        try:
            os.remove(self.SPECIALMARKER)
        except FileNotFoundError:
            pass
