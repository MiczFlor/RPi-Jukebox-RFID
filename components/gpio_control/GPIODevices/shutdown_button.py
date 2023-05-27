import time
from RPi import GPIO
import logging
try:
    from simple_button import SimpleButton, print_edge_key, print_pull_up_down
except ImportError:
    from .simple_button import SimpleButton, print_edge_key, print_pull_up_down

logger = logging.getLogger(__name__)


class ShutdownButton(SimpleButton):

    def __init__(self, pin, action=lambda *args: None, name=None, bouncetime=500, antibouncehack=False, edge='falling',
                 led_pin=None, hold_time=3.0, pull_up_down='pull_up', iteration_time=.2):
        self.led_pin = led_pin
        self.iteration_time = iteration_time
        if self.led_pin is not None:
            GPIO.setup(self.led_pin, GPIO.OUT)
        super(ShutdownButton, self).__init__(pin=pin, action=action, name=name, bouncetime=bouncetime,
                                             antibouncehack=antibouncehack, edge=edge, hold_time=hold_time,
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
        if self.is_pressed: # Should not be necessary, but handler gets called on rising edge too
           logger.debug('ShutdownButton pressed, ensuring long press for {} seconds, checking each {}s'.format(
               self.hold_time, self.iteration_time
           ))
           t_passed = 0
           led_state = True
           while t_passed < self.hold_time:
               self.set_led(led_state)
               time.sleep(self.iteration_time)
               t_passed += self.iteration_time
               led_state = not led_state
               if not self.is_pressed:
                   break
           if t_passed >= self.hold_time:
               # trippel off period to indicate command accepted
               self.set_led(GPIO.HIGH)
               time.sleep(.6)
               # leave it on for the moment, it will be off when the system is down
               self.when_pressed(*args)
           else:
               # leave LED on if pressing was cancelled early (during flashing) and status led uses the same pin as shutdown led
               if status_led.GPIO and (status_led.GPIO is self.led_pin):
                  self.set_led(GPIO.HIGH)
               else:
                  self.set_led(GPIO.LOW)
                  

    def __repr__(self):
        return '<ShutdownButton-{}(pin={},hold_time={},iteration_time={},led_pin={},edge={},bouncetime={},antibouncehack={},pull_up_down={})>'.format(
            self.name, self.pin, self.hold_time, self.iteration_time, self.led_pin, print_edge_key(self.edge), self.bouncetime,self.antibouncehack, print_pull_up_down(self.pull_up_down)
        )
