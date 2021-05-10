import time
from signal import pause
import logging
import RPi.GPIO as GPIO
GPIO.setmode(GPIO.BCM)

logger = logging.getLogger(__name__)

map_edge_parse = {'falling':GPIO.FALLING, 'rising':GPIO.RISING, 'both':GPIO.BOTH}
map_pull_parse = {'pull_up':GPIO.PUD_UP, 'pull_down':GPIO.PUD_DOWN, 'pull_off':GPIO.PUD_OFF}
map_edge_print = {GPIO.FALLING: 'falling', GPIO.RISING: 'rising', GPIO.BOTH: 'both'}
map_pull_print = {GPIO.PUD_UP:'pull_up', GPIO.PUD_DOWN: 'pull_down', GPIO.PUD_OFF: 'pull_off'}

def parse_edge_key(edge):
    if edge in [GPIO.FALLING, GPIO.RISING, GPIO.BOTH]:
        return edge
    try:
        result = map_edge_parse[edge.lower()]
    except KeyError:
        result = edge
        raise KeyError('Unknown Edge type {edge}'.format(edge=edge))
    return result

def parse_pull_up_down(pull_up_down):
    if pull_up_down in [GPIO.PUD_UP, GPIO.PUD_DOWN, GPIO.PUD_OFF]:
        return pull_up_down
    try:
        result = map_pull_parse[pull_up_down]
    except KeyError:
        result = pull_up_down
        raise KeyError('Unknown Pull Up/Down type {pull_up_down}'.format(pull_up_down=pull_up_down))
    return result

def print_edge_key(edge):
    try:
        result = map_edge_print[edge]
    except KeyError:
        result = edge
    return result

def print_pull_up_down(pull_up_down):
    try:
        result = map_pull_print[pull_up_down]
    except KeyError:
        result = pull_up_down
    return result

# This function takes a holding time (fractional seconds), a channel, a GPIO state and an action reference (function).
# It checks if the GPIO is in the state since the function was called. If the state
# changes it return False. If the time is over the function returns True.
def checkGpioStaysInState(holdingTime, gpioChannel, gpioHoldingState):
    # Get a reference start time (https://docs.python.org/3/library/time.html#time.perf_counter)
    startTime = time.perf_counter()
    # Continously check if time is not over
    while True:
        currentState = GPIO.input(gpioChannel)
        if holdingTime < (time.perf_counter() - startTime):
            break
        # Return if state does not match holding state
        if (gpioHoldingState != currentState):
            return False
        # Else: Wait

    if (gpioHoldingState != currentState):
        return False
    return True


class SimpleButton:
    def __init__(self, pin, action=lambda *args: None, name=None, bouncetime=500, antibouncehack=False,
                 edge=GPIO.FALLING, hold_time=.1, hold_repeat=False, pull_up_down=GPIO.PUD_UP):
        self.edge = parse_edge_key(edge)
        self.hold_time = hold_time
        self.hold_repeat = hold_repeat
        self.pull_up = True
        self.pull_up_down = parse_pull_up_down(pull_up_down)

        self.pin = pin
        self.name = name
        self.bouncetime = bouncetime
        self.antibouncehack = antibouncehack
        GPIO.setup(self.pin, GPIO.IN, pull_up_down=self.pull_up_down)
        self._action = action
        GPIO.add_event_detect(self.pin, edge=self.edge, callback=self.callbackFunctionHandler,
                              bouncetime=self.bouncetime)
        self.callback_with_pin_argument = False

    def callbackFunctionHandler(self, *args):
        if len(args) > 0 and args[0] == self.pin and not self.callback_with_pin_argument:
            logger.debug('Remove pin argument by callbackFunctionHandler - args before: {}'.format(args))
            args = args[1:]
            logger.debug('args after: {}'.format(args))

        if self.antibouncehack: 
            time.sleep(0.1)
            inval = GPIO.input(self.pin)
            if inval != GPIO.LOW:
                return None

        if self.hold_repeat:
            return self.holdAndRepeatHandler(*args)
        logger.info('{}: execute callback'.format(self.name))
        return self.when_pressed(*args)

    @property
    def when_pressed(self):
        logger.info('{}: action'.format(self.name))
        return self._action

    @when_pressed.setter
    def when_pressed(self, func):
        logger.info('{}: set when_pressed')
        self._action = func

        GPIO.remove_event_detect(self.pin)
        self._action = func
        logger.info('add new action')
        GPIO.add_event_detect(self.pin, edge=self.edge, callback=self.callbackFunctionHandler, bouncetime=self.bouncetime)

    def set_callbackFunction(self, callbackFunction):
        self.when_pressed = callbackFunction

    def holdAndRepeatHandler(self, *args):
        logger.info('{}: holdAndRepeatHandler'.format(self.name))
        # Rise volume as requested
        self.when_pressed(*args)
        # Detect holding of button
        while checkGpioStaysInState(self.hold_time, self.pin, GPIO.LOW):
            self.when_pressed(*args)

    def __del__(self):
        logger.debug('remove event detection')
        GPIO.remove_event_detect(self.pin)

    @property
    def is_pressed(self):
        if self.pull_up:
            return not GPIO.input(self.pin)
        return GPIO.input(self.pin)

    def __repr__(self):
        return '<SimpleButton-{}(pin={},edge={},hold_repeat={},hold_time={},bouncetime={},antibouncehack={},pull_up_down={})>'.format(
            self.name, self.pin, print_edge_key(self.edge), self.hold_repeat, self.hold_time, self.bouncetime,self.antibouncehack,print_pull_up_down(self.pull_up_down)
        )


if __name__ == "__main__":
    print('please enter pin no to test')
    pin = int(input())
    func = lambda *args: print('FunctionCall with {}'.format(args))
    btn = SimpleButton(pin=pin, action=func, hold_repeat=True)
    pause()
