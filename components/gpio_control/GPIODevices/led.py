import logging
import time
from os import system

from RPi import GPIO

GPIO.setmode(GPIO.BCM)

logger = logging.getLogger(__name__)


class LED:
    def __init__(self, pin, initial_value=True, name='LED'):
        self.pin = pin
        self.name = name
        logger.debug('initialize {}(pin={}) to off'.format(self.name, self.pin))
        GPIO.setup(self.pin, GPIO.OUT)
        GPIO.output(self.pin, initial_value)

    def on(self):
        logger.debug('Set Output of {}(pin={}) to on'.format(self.name, self.pin))
        GPIO.output(self.pin, GPIO.HIGH)

    def off(self):
        logger.debug('Set Output of {}(pin={}) to off'.format(self.name, self.pin))
        GPIO.output(self.pin, GPIO.LOW)

    def status(self):
        return GPIO.input(self.pin)


class StatusLED(LED):
    logger = logging.getLogger("StatusLED")

    def __init__(self, pin, name='StatusLED'):
        super(StatusLED, self).__init__(pin, initial_value=False, name=name)
        self.logger.info('Waiting for phoniebox-startup-scripts service to be active')
        systemctlCmd = 'systemctl is-active --quiet phoniebox-startup-scripts.service'
        while system(systemctlCmd) != 0:
            self.logger.debug('phoniebox-startup-scripts service not yet active')
            time.sleep(1)
        self.logger.info('phoniebox-startup-scripts service active')
        self.on()
