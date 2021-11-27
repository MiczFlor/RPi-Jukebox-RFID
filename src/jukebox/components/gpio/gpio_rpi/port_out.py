import RPi.GPIO as GPIO
import logging
import threading


class PortOut:
    def __new__(cls, name, config, config_name):
        instance = super(PortOut, cls).__new__(cls)
        return instance

    def __init__(self, name, config, config_name):
        self._logger = logging.getLogger('jb.gpio')
        self.states = config['States']
        self.pins = config['Pins']
        self.name = name
        self.type = config['Type']
        initial_state = config.get('Pins', default=list(self.states.keys())[0])

        for pin in self.pins:
            GPIO.setup(pin, GPIO.OUT)
            self.SetPortState(initial_state)

        self._seq_timer = None
        self._seq_cancel = False

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

    def _run_sequence(self):
        if self._seq_cancel:
            return

        e = self.seq[self.seq_ptr]
        self.seq_ptr += 1

        s = self.SetPortState(e[0])
        if s is not None:
            delay = e[1]

            if self.seq_ptr >= self.seq_len:
                self.seq_ptr = 0

                if self.seq_mode == 'single':
                    self._seq_cancel = True
                    return

            self._seq_timer = threading.Timer(delay / 1000, self._run_sequence)
            self._seq_timer.start()
        else:
            self._logger.debug("State is not existing")

    def StartPortSequence(self, seq):
        if (self._seq_cancel is False):
            self.StopPortSequence()
        self._seq_cancel = False
        self.seq_mode = seq.get('mode')
        self.seq = seq.get('seq')
        self.seq_len = len(self.seq)
        self.seq_ptr = 0
        self._run_sequence()
        return (0)

    def StopPortSequence(self):
        self._seq_cancel = True
        if self._seq_timer is not None:
            self._seq_timer.cancel()
        return (0)

    def stop(self):
        self.StopPortSequence()
        pass
