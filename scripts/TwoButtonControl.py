from scripts.SimpleButton import SimpleButton
from scripts.gpio_control import logger


def functionCallTwoButtons(btn1, btn2, functionCall1, functionCallBothPressed=None):
    def functionCallTwoButtons(*args):
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
            callbackFunction=lambda *args: None,
            name=name+'Btn2', bouncetime=500, edge=GPIO.FALLING, hold_time=hold_time, hold_repeat=hold_repeat)

        self.btn2 = SimpleButton(bcmPin2, pull_up=pull_up, hold_time=hold_time, hold_repeat=hold_repeat,
                                 name=name+'Btn2', bouncetime=500, edge=GPIO.FALLING)
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
