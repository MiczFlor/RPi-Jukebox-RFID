try:
    from simple_button import SimpleButton
except ImportError:
    from .simple_button import SimpleButton
from RPi import GPIO
import logging
logger = logging.getLogger(__name__)

GPIO.setmode(GPIO.BCM)


def functionCallTwoButtons(btn1, btn2, functionCall1, functionCall2, functionCallBothPressed=None):
    def functionCallTwoButtons(*args):
        btn1_pressed = btn1.is_pressed
        btn2_pressed = btn2.is_pressed
        logger.debug('Btn1 {}, Btn2 {}'.format(btn1_pressed, btn2_pressed))
        if btn1_pressed and btn2_pressed:
            logger.debug("Both buttons was pressed")
            if functionCallBothPressed is not None:
                logger.debug("Both Btns are pressed, action: functionCallBothPressed")
                logger.info('functionCallBoth')
                return functionCallBothPressed(*args)
            logger.debug('No two button pressed action defined')
        elif btn1_pressed:
            logger.debug("Btn1 is pressed, secondary Btn not pressed, action: functionCall1")
            logger.info('functionCall1')
            return functionCall1(*args)
        elif btn2_pressed:
            logger.debug("Btn2 is pressed, action: functionCall2")
            logger.info('functionCall2')
            return functionCall2(*args)
        else:
            logger.debug("No Button Pressed: no action")
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
            name=name + 'Btn2',
            bouncetime=500,
            edge=GPIO.FALLING,
            hold_time=hold_time,
            hold_repeat=hold_repeat)

        self.btn2 = SimpleButton(pin=bcmPin2,
                                 action=lambda *args: None,
                                 hold_time=hold_time,
                                 hold_repeat=hold_repeat,
                                 name=name + 'Btn2',
                                 bouncetime=500,
                                 edge=GPIO.FALLING)
        generatedTwoButtonFunctionCall = functionCallTwoButtons(self.btn1,
                                                                self.btn2,
                                                                self.functionCallBtn1,
                                                                self.functionCallBtn2,
                                                                self.functionCallTwoBtns
                                                                )
        self.action = generatedTwoButtonFunctionCall
        logger.info('adding new action')
        self.btn1.when_pressed = generatedTwoButtonFunctionCall
        self.btn2.when_pressed = generatedTwoButtonFunctionCall
        self.name = name

    def __repr__(self):
        two_btns_action = self.functionCallTwoBtns is not None
        return '<TwoBtnControl-{name}({bcmPin1}, {bcmPin2},two_buttons_action={two_btns_action})>'.format(
            name=self.name,
            bcmPin1=self.bcmPin1,
            bcmPin2=self.bcmPin2,
            two_btns_action=two_btns_action
        )


if __name__ == "__main__":
    logging.basicConfig(level='INFO')
    pin1 = int(input('please enter first pin'))
    pin2 = int(input('please enter second pin'))
    func1 = lambda *args: print('Function Btn1 executed with {}'.format(args))
    func2 = lambda *args: print('Function Btn2 executed with {}'.format(args))
    func3 = lambda *args: print('Function BothBtns executed with {}'.format(args))
    two_btn_control = TwoButtonControl(pin1, pin2, func1, func2, func3)

    print('running')
    while True:
        pass
