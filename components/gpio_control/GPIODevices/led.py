import logging
import time

import mpd
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


class MPDStatusLED(LED):
    logger = logging.getLogger("MPDStatusLED")

    def __init__(self, pin, host='localhost', port=6600, name='MPDStatusLED'):
        super(MPDStatusLED, self).__init__(pin, initial_value=False, name=name)
        self.mpc = mpd.MPDClient()
        self.host = host
        self.port = port
        self.logger.info('Waiting for MPD Connection on {}:{}'.format(
            self.host, self.port))
        while not self.has_mpd_connection():
            self.logger.debug('No MPD Connection yet established')
            time.sleep(1)
        self.logger.info('Connection to MPD server on host {}:{} established'.format(self.host, self.port))
        self.on()

    def has_mpd_connection(self):
        self.mpc.disconnect()
        try:
            self.mpc.connect(self.host, self.port)
            self.mpc.ping()
            self.mpc.disconnect()
            return True
        except ConnectionError:
            return False
