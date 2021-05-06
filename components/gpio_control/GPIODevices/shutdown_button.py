import math
import time
from RPi import GPIO
import logging
try:
    from simple_button import SimpleButton
except ImportError:
    from .simple_button import SimpleButton

logger = logging.getLogger(__name__)


class ShutdownButton(SimpleButton):

    def __init__(self, pin, action=lambda *args: None, name=None, bouncetime=500, edge=GPIO.FALLING,
                 led_pin=None, time_pressed=2, pull_up_down=GPIO.PUD_UP, iteration_time=.2):
        self.led_pin = led_pin
        self.time_pressed = time_pressed
        self.iteration_time = iteration_time
        if self.led_pin is not None:
            GPIO.setup(self.led_pin, GPIO.OUT)
        super(ShutdownButton, self).__init__(pin=pin, action=action, name=name, bouncetime=bouncetime, edge=edge,
                                             pull_up_down=pull_up_down
                                             )
        pass

    # function to provide user feedback (= flashing led) while the shutdown button is pressed
    # do not directly call shutdown, in case it was hit accedently
    # shutdown is only issued when the button remains pressed for all interations of the for loop
    def set_led(self, status):
        if self.led_pin is not None:
            logger.debug('set LED on pin {} to {}'.format(self.led_pin, status))
            GPIO.output(self.led_pin, status)
        else:
            logger.debug('cannot set LED to {}: no LED pin defined'.format(status))

    def callbackFunctionHandler(self, *args):
        cancelled = False
        n_checks = math.ceil(self.time_pressed / self.iteration_time)
        logger.debug('ShutdownButton pressed, ensuring long press for {} seconds, checking each {}s: {}'.format(
            self.time_pressed, self.iteration_time, n_checks
        ))
        for x in range(n_checks):
            self.set_led(x & 1)
            time.sleep(.2)
            cancelled = not self.is_pressed
            if cancelled:
                break
        if not cancelled:
            # trippel off period to indicate command accepted
            time.sleep(.6)
            self.set_led(GPIO.HIGH)
            # leave it on for the moment, it will be off when the system is down
            self.when_pressed(*args)
        else:
            # switch off LED if pressing was cancelled early (during flashing)
            self.set_led(GPIO.LOW)

    def __repr__(self):
        return '<ShutdownButton-{}(pin {},time_pressed={},iteration_time={},led_pin={})>'.format(
            self.name, self.pin, self.time_pressed, self.iteration_time, self.led_pin
        )
