from SimpleButton import SimpleButton
from RPi import GPIO
import logging
logger = logging.getLogger(__name__)

GPIO.setmode(GPIO.BCM)


def functionCallTwoButtons(btn1, btn2, functionCall1, functionCall2, functionCallBothPressed=None):
    def functionCallTwoButtons(*args):
        if btn1.is_pressed and btn2.is_pressed:
            logger.debug("Both buttons was pressed")
            if functionCallBothPressed is not None:
                logger.debug("Both Btns are pressed, action: functionCallBothPressed")
                return functionCallBothPressed(*args)
            logger.debug('No two button pressed action defined')
        elif btn1.is_pressed:
            logger.debug("Btn1 is pressed, secondary Btn not pressed, action: functionCall1")
            return functionCall1(*args)
        elif btn2.is_pressed:
            logger.debug("Btn2 is not pressed, action: functionCall2")
            return functionCall2(*args)
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
        self.btn1 = SimpleButton(
            pin=bcmPin1,
            action=lambda *args: None,
            name=name+'Btn2',
            bouncetime=500,
            edge=GPIO.FALLING,
            hold_time=hold_time,
            hold_repeat=hold_repeat)

        self.btn2 = SimpleButton(pin=bcmPin2,
                                 action=lambda *args: None,
                                 hold_time=hold_time,
                                 hold_repeat=hold_repeat,
                                 name=name+'Btn2',
                                 bouncetime=500,
                                 edge=GPIO.FALLING)
        generatedTwoButtonFunctionCall = functionCallTwoButtons(self.btn1,
                                                                self.btn2,
                                                                self.functionCallBtn1,
                                                                self.functionCallBtn2,
                                                                self.functionCallTwoBtns
                                                                )

        self.btn1.action = generatedTwoButtonFunctionCall
        self.btn2.action = generatedTwoButtonFunctionCall
        self.name = name

    def __repr__(self):
        two_btns_action = self.functionCallTwoBtns is not None
        return f'<TwoBtnControl-{self.name}({self.bcmPin1}, {self.bcmPin2},two_buttons_action={two_btns_action})>'
