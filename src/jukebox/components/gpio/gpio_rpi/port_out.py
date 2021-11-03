import RPi.GPIO as GPIO
import logging

logger = logging.getLogger('jb.gpio')


class PortOut:

    def __init__(self, name, config):
        self.states = config['States']
        self.pins = config['Pins']
        self.name = name
        initial_state = config.get('Pins', default=self.states[0])

        for pin in self.pins:
            GPIO.setup(pin, GPIO.OUT)
            self.SetPort(self, initial_state)

    def SetPortState(self, state):

        pin_state = self.states.get(state)

        for i, pin in enumerate(self.pins):
            if pin_state[i] == 1:
                level = GPIO.HIGH
            else:
                level = GPIO.LOW

            GPIO.output(pin, level)

        return 0

    def StartPortSequence(self, seq):

        # for step in seq:
        #    time.sleep(step['delay'] / 1000)
        #    self.SetPort(step['state'])

        # {1: {'delay',100,'pin':'xxx','state':1},
        #  2: {'delay',100,'pin':'xxx','state':0}}

        # {1: {'delay',100,'pin':'xxx','state':1},
        #  2: {'repeat',100,'pin':'xxx','state':0}}

        return (0)

    def StopPortSequence(self):
        return (0)
