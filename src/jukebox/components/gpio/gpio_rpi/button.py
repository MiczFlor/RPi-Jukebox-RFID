import time
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


def checkGpioIsInState(gpioChannel, gpioHoldingState):
    time.sleep(0.1)
    currentState = GPIO.input(gpioChannel)
    if (gpioHoldingState != currentState):
        return False
    return True


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
    def __new__(cls, name, config, config_name):
        instance = None
        pin = config.get('Pin')
        function = config.get('Function')

        if pin is None:
            logger.error(f"Pin has to be specified for \"{name}\"{config.lc} in {config_name}")
        elif function is None:
            logger.error(f"FunctionCW required for \"{name}\"{config.lc} in {config_name}")
        else:
            instance = super(Button, cls).__new__(cls)
            instance.pin = pin
            instance._action = function
        return instance

    def __init__(self, name, config, config_name):
        self._logger = logger

        self.name = name

        self.edge = parse_edge_key(config.get('edge', default='falling'))
        if self.edge == GPIO.FALLING:
            self.active_level = GPIO.LOW
        else:
            self.active_level = GPIO.HIGH
        self.hold_time = config.get('hold_time', default='0.3')
        self.hold_mode = config.get('hold_mode', default=None)
        self.pull_up_down = parse_pull_up_down(config.get('pull_up_down', default='pull_down'))

        self.bouncetime = config.get('bouncetime', default=500)
        self.antibouncehack = config.get('antibouncehack', default=False)
        self._action2 = config.get('Function2', default=None)

        GPIO.setup(self.pin, GPIO.IN, pull_up_down=self.pull_up_down)
        GPIO.add_event_detect(self.pin, edge=self.edge, callback=self.callbackFunctionHandler, bouncetime=self.bouncetime)
        self.callback_with_pin_argument = False
        self._cancel = False

    def callbackFunctionHandler(self, *args):
        if len(args) > 0 and args[0] == self.pin and not self.callback_with_pin_argument:
            self._logger.debug('Remove pin argument by callbackFunctionHandler - args before: {}'.format(args))
            args = args[1:]
            self._logger.debug('args after: {}'.format(args))

        if self.antibouncehack:
            time.sleep(0.1)
            inval = GPIO.input(self.pin)
            if inval != self.active_level:
                return None

        if self.hold_mode in ('Repeat', 'Postpone', 'SecondFunc', 'SecondFuncRepeat'):
            return self.longPressHandler()
        else:
            self._logger.info('{}: execute callback'.format(self.name))
            return utils.decode_and_call_rpc_command(self._action, self._logger)

    def longPressHandler(self): # noqa: C901
        self._logger.info('{}: longPressHandler, mode: {}'.format(self.name, self.hold_mode))
        # instant action (except Postpone mode)
        if self.hold_mode != "Postpone":
            ret = utils.decode_and_call_rpc_command(self._action, self._logger)

        # action(s) after hold_time
        if self.hold_mode == "Repeat":
            # Repeated call of main action (multiple times if button is held long enough)
            while checkGpioStaysInState(self.hold_time, self.pin, self.active_level):
                if self._cancel:
                    break
                ret = utils.decode_and_call_rpc_command(self._action, self._logger)

        elif self.hold_mode == "Postpone":
            # Postponed call of main action (once)
            if checkGpioStaysInState(self.hold_time, self.pin, self.active_level):
                ret = utils.decode_and_call_rpc_command(self._action, self._logger)
            while checkGpioIsInState(self.pin, self.active_level):
                if self._cancel:
                    break

        elif self.hold_mode == "SecondFunc":
            # Call of secondary action (once)
            if checkGpioStaysInState(self.hold_time, self.pin, self.active_level):
                ret = utils.decode_and_call_rpc_command(self._action2, self._logger)
            while checkGpioIsInState(self.pin, self.active_level):
                if self._cancel:
                    break

        elif self.hold_mode == "SecondFuncRepeat":
            # Repeated call of secondary action (multiple times if button is held long enough)
            while checkGpioStaysInState(self.hold_time, self.pin, self.active_level):
                if self._cancel:
                    break
                ret = utils.decode_and_call_rpc_command(self._action, self._logger)
        return ret

    def stop(self):
        self._logger.debug('remove event detection for: {}'.format(self.name))
        GPIO.remove_event_detect(self.pin)
        self._cancel = True
        time.sleep(0.1)
