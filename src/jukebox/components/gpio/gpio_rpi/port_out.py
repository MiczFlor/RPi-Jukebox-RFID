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

    def _run_sequence(self):
        e = self.seq[self.seq_steps[self.seq_ptr]]
        
        self.seq_ptr += 1

        if self.seq_ptr >= self.seq_len:
            self.seq_ptr = 0
            # stop sequece
        else:

            s = e.get('state')
            if s is not None:
                delay = e.get('repeat')
                if delay is not None:
                    func = 'r'
                    self.seq_ptr = 0
                else:
                    delay = e.get('delay')
                    if delay is not None:
                        func = 'd'
                    else:
                        func = None
                
                if func is not None:
                    t = Timer(delay/1000, self._run_sequence)
                    t.start()
                else:
                    # log error, 
                    # stop seqence
                    pass
            else:
                # log error, 
                # stop seqence
                pass

    
    def StartPortSequence(self, seq):
        self.seq = seq  # maybe deepcopy this?

        self.seq_steps = seq.keys()
        self.seq_len = len(self.seq_steps)

        self.seq_ptr = 0


        
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
