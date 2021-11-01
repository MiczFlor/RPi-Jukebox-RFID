import time
from signal import pause
import logging
import jukebox.utils as utils

try:
    import RPi.GPIO as GPIO
    GPIO.setmode(GPIO.BCM)
except ImportError:
    pass

logger = logging.getLogger('jb.gpio')

map_edge_parse = {'falling': GPIO.FALLING, 'rising': GPIO.RISING, 'both': GPIO.BOTH}
map_pull_parse = {'pull_up': GPIO.PUD_UP, 'pull_down': GPIO.PUD_DOWN, 'pull_off': GPIO.PUD_OFF}
map_edge_print = {GPIO.FALLING: 'falling', GPIO.RISING: 'rising', GPIO.BOTH: 'both'}
map_pull_print = {GPIO.PUD_UP: 'pull_up', GPIO.PUD_DOWN: 'pull_down', GPIO.PUD_OFF: 'pull_off'}


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
        time.sleep(0.1)
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


class Button:
    def __init__(self, pin, action=lambda *args: None, action2=lambda *args: None, name=None,
                 bouncetime=500, antibouncehack=False, edge='falling', hold_time=.3, hold_mode=None, pull_up_down='pull_up'):
        self._logger = logger
        self.edge = parse_edge_key(edge)
        self.hold_time = hold_time
        self.hold_mode = hold_mode
        self.pull_up = True
        self.pull_up_down = parse_pull_up_down(pull_up_down)

        self.pin = pin
        self.name = name
        self.bouncetime = bouncetime
        self.antibouncehack = antibouncehack
        GPIO.setup(self.pin, GPIO.IN, pull_up_down=self.pull_up_down)
        self._action = action
        self._action2 = action2
        GPIO.add_event_detect(self.pin, edge=self.edge, callback=self.callbackFunctionHandler,
                              bouncetime=self.bouncetime)
        self.callback_with_pin_argument = False

    def callbackFunctionHandler(self, *args):
        if len(args) > 0 and args[0] == self.pin and not self.callback_with_pin_argument:
            self._logger.debug('Remove pin argument by callbackFunctionHandler - args before: {}'.format(args))
            args = args[1:]
            self._logger.debug('args after: {}'.format(args))

        if self.antibouncehack:
            time.sleep(0.1)
            inval = GPIO.input(self.pin)
            if inval != GPIO.LOW:
                return None

        if self.hold_mode in ('Repeat', 'Postpone', 'SecondFunc', 'SecondFuncRepeat'):
            return self.longPressHandler()
        else:
            logger.info('{}: execute callback'.format(self.name))
            return utils.decode_and_call_rpc_command(self._action, self._logger)

#    @property
#    def when_pressed(self):
#        self._logger.info('{}: action'.format(self.name))
#        return self._action

#    @property
#    def when_held(self):
#        self._logger.info('{}: action2'.format(self.name))#
#
#        action = utils.decode_rpc_command(self._action2, self._logger)
#        if action is not None:
#            plugs.call_ignore_errors(action['package'], action['plugin'],
#                                     action['method'], args=action['args'], kwargs=action['kwargs'])#
#
#        return self._action2

#   @when_pressed.setter
#   def when_pressed(self, func):
#       logger.info('{}: set when_pressed')
#       self._action = func##

#       GPIO.remove_event_detect(self.pin)
#       logger.info('add new action')
#       GPIO.add_event_detect(self.pin, edge=self.edge, callback=self.callbackFunctionHandler, bouncetime=self.bouncetime)

#   def set_callbackFunction(self, callbackFunction):
#       self.when_pressed = callbackFunction

    def longPressHandler(self):
        logger.info('{}: longPressHandler, mode: {}'.format(self.name, self.hold_mode))
        # instant action (except Postpone mode)
        if self.hold_mode != "Postpone":
            utils.decode_and_call_rpc_command(self._action, self._logger)

        # action(s) after hold_time
        if self.hold_mode == "Repeat":
            # Repeated call of main action (multiple times if button is held long enough)
            while checkGpioStaysInState(self.hold_time, self.pin, GPIO.LOW):
                ret = utils.decode_and_call_rpc_command(self._action, self._logger)

        elif self.hold_mode == "Postpone":
            # Postponed call of main action (once)
            if checkGpioStaysInState(self.hold_time, self.pin, GPIO.LOW):
                ret = utils.decode_and_call_rpc_command(self._action, self._logger)
            while checkGpioStaysInState(self.hold_time, self.pin, GPIO.LOW):
                pass

        elif self.hold_mode == "SecondFunc":
            # Call of secondary action (once)
            if checkGpioStaysInState(self.hold_time, self.pin, GPIO.LOW):
                ret = utils.decode_and_call_rpc_command(self._action2, self._logger)
            while checkGpioStaysInState(self.hold_time, self.pin, GPIO.LOW):
                pass

        elif self.hold_mode == "SecondFuncRepeat":
            # Repeated call of secondary action (multiple times if button is held long enough)
            while checkGpioStaysInState(self.hold_time, self.pin, GPIO.LOW):
                ret = utils.decode_and_call_rpc_command(self._action, self._logger)
        return ret

    def __del__(self):
        logger.debug('remove event detection')
        GPIO.remove_event_detect(self.pin)

    @property
    def is_pressed(self):
        if self.pull_up:
            return not GPIO.input(self.pin)
        return GPIO.input(self.pin)

    def __repr__(self):
        return '<SimpleButton-{}(pin={},edge={},hold_mode={},hold_time={},bouncetime={},antibouncehack={},pull_up_down={})>'.\
               format(self.name, self.pin, print_edge_key(self.edge), self.hold_mode, self.hold_time, self.bouncetime,
               self.antibouncehack, print_pull_up_down(self.pull_up_down))


if __name__ == "__main__":
    print('please enter pin no to test')
    pin = int(input())
    func = lambda *args: print('FunctionCall with {}'.format(args))
    btn = Button(pin=pin, action=func, hold_mode='Repeat')
    pause()
