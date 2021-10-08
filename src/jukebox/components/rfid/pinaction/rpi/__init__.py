import logging
import time
import threading
import jukebox.cfghandler
import jukebox.plugs as plugs
from typing import Optional
import RPi.GPIO as gpio

logger = logging.getLogger('jb.rfid.buzz')
cfg = jukebox.cfghandler.get_handler('rfid')


class PinActionClass(threading.Thread):
    """
    A thread to control a GPIO output pin to sound a buzzer or light an LED

    An extra thread for a GPIO pin? Why so complicated?
    Reason 1: This is a single thread for all RFID reader threads (if there is more than one), because we only
    have a single GPIO pin and access must be properly sequenced to ensure it is reset after sounding the buzzer
    Reason 2: The time the buzzer is sounded should be run in background to avoid extra delay between card placement and
    card action however small the buzzer duration

    Note: You can connect a LED or a Piezzo Buzzer. Only for reasons of simplicity, parameters are named 'buzzer'

    The GPIO level is active high, after a card has been detected for the length of buzz_duration
    """
    # https://sourceforge.net/p/raspberry-gpio-python/wiki/BasicUsage/
    def __init__(self):
        """

        :param buzz_pin: The GPIO pin of the buzzer of LED
        :param buzz_duration: The duration in sec the GPIO pin is high after a card has been detected (e.g. 0.2)
        :param buzz_retrigger: If True, multiple cards within the buzz_duration start the buzzer time anew
        """
        super().__init__(name='RfidPinAction', daemon=True)
        self.trigger = threading.Event()

        # Use an invalid buzz pin as default pin
        self.buzz_pin = cfg.setndefault('rfid.pinaction.rpi', 'pin', 0)
        self.buzz_delay = cfg.setndefault('rfid.pinaction.rpi', 'duration', 0.2)
        buzz_retrigger = cfg.setndefault('rfid.pinaction.rpi', 'retrigger', False)
        logger.debug(f"PinActionClass started with pin='{self.buzz_pin}', duration='{self.buzz_delay}', "
                     f"retrigger='{buzz_retrigger}'")

        if buzz_retrigger:
            self.run_action = self.run_retrigger
        else:
            self.run_action = self.run_single_trigger

        # Initialize RPi.GPIO here, as this is only required when a buzzer is configured
        gpio.setmode(gpio.BCM)
        gpio.setup(self.buzz_pin, gpio.OUT, initial=gpio.LOW)
        gpio.output(self.buzz_pin, gpio.LOW)

    def run_retrigger(self) -> None:
        """
        The wait-for-trigger-and-do-it endless loop for the re-triggerable case
        """
        while True:
            self.trigger.wait()
            # Clear the trigger, so we can detect a new event while doing the pin high wait
            self.trigger.clear()
            gpio.output(self.buzz_pin, gpio.HIGH)
            # Wait for duration unless, another trigger event already comes in
            self.trigger.wait(self.buzz_delay)
            # Set the pin low for a very small length of time, to provide a feedback that card re-trigger has happend
            gpio.output(self.buzz_pin, gpio.LOW)
            time.sleep(0.1)

    def run_single_trigger(self) -> None:
        """
        The wait-for-trigger-and-do-it endless loop for the non re-triggerable case
        """
        while True:
            self.trigger.wait()
            gpio.output(self.buzz_pin, gpio.HIGH)
            # A blocking wait to ignore changes on trigger
            time.sleep(self.buzz_delay)
            gpio.output(self.buzz_pin, gpio.LOW)
            # Only clear the trigger after full delay time, to also clear any trigger that came in during the wait
            self.trigger.clear()

    def run(self):
        self.run_action()

    def cleanup(self):
        """
        The abort handler to ensure pin is low active on exit

        Note: This does not get called automatically. It needs to be taken care of on program exit!
        """
        gpio.output(self.buzz_pin, gpio.LOW)
        gpio.cleanup(self.buzz_pin)


_handler: Optional[PinActionClass] = None


def get_handler():
    global _handler
    if 'rfid.pinaction.rpi' in cfg:
        enabled = cfg.setndefault('rfid.pinaction.rpi', 'enabled', value=False)
        if enabled is True and _handler is None:
            _handler = PinActionClass()
    else:
        logger.error("Missing config section for 'rfid.pinaction.rpi'. Disabling myself...")
    return _handler


@plugs.atexit
def atexit(signal: int):
    if _handler is not None:
        _handler.cleanup()
