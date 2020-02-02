import time

import RPi.GPIO as GPIO


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
    def callbackFunctionHandler(self):
        if self.hold_repeat:
            return self.holdAndRepeatHandler
        return self.when_pressed

    def __init__(self, pin, action=lambda *args: None, name=None, bouncetime=500, edge=GPIO.FALLING,
                 hold_time=.1, hold_repeat=False):
        self.edge = parse_edge_key(edge)
        self.hold_time = hold_time
        self.hold_repeat = hold_repeat

        self.pin = pin
        self.name = name
        self.bouncetime = bouncetime
        GPIO.setup(self.pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        self.when_pressed = action
        GPIO.add_event_detect(channel=self.pin, edge=self.edge, callback=self.callbackFunctionHandler,
                              bouncetime=self.bouncetime)

    def set_callbackFunction(self, callbackFunction):
        self.when_pressed = callbackFunction

    def holdAndRepeatHandler(self, channel):
        # Rise volume as requested
        self.when_pressed(channel)
        # Detect holding of button
        while checkGpioStaysInState(self.hold_time, self.pin, GPIO.LOW):
            self.when_pressed(channel)

    def __del__(self):
        GPIO.remove_event_detect(self.pin)

    @property
    def is_pressed(self):
        return GPIO.input(self.pin)
