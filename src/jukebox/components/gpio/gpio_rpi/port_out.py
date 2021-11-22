import RPi.GPIO as GPIO
import logging

logger = logging.getLogger('jb.gpio')


class PortOut:
    def __new__(cls, name, config, config_name):
        instance = super(PortOut, cls).__new__(cls)
        return instance

    def __init__(self, name, config, config_name):
        self.states = config['States']
        self.pins = config['Pins']
        self.name = name
        self.type = config['Type']
        initial_state = config.get('Pins', default=list(self.states.keys())[0])

        for pin in self.pins:
            GPIO.setup(pin, GPIO.OUT)
            self.SetPortState(initial_state)

    def SetPortState(self, state):

        pin_state = self.states.get(state)

        if pin_state is not None:
            for i, pin in enumerate(self.pins):
                if pin_state[i] == 1:
                    level = GPIO.HIGH
                else:
                    level = GPIO.LOW

                GPIO.output(pin, level)

        return state

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

    def stop(self):
        self.StopPortSequence()
        pass
