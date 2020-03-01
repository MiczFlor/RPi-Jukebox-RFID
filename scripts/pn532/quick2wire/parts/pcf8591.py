"""
API for the PCF8591 I2C A/D D/A converter.

The PCF8591 chip has four physical input pins, named AIN0 to AIN3, at
which it measures voltage, and a single physical output pin, named
AOUT, at which it generates analogue output.

Applications  control the  chip by  setting  or getting  the state  of
logical channels that the chip maps to its physical pins. There is one
output channel and  up to four input channels,  depending on the mode.
Input channels  are either _single-ended_, measuring the  voltage on a
input pin, or _differential_, measuring the voltage difference between
two input pins.

Applications talk to the chip via objects of the PCF8591 class. A
PCF8591 object is created with an I2CMaster, through which it
communicates with the chip, and a mode, one of:

FOUR_SINGLE_ENDED -- four single-ended channels reporting voltage at
                     AIN0 to AIN3, no differential inputs.

THREE_DIFFERENTIAL -- three differential inputs reporting voltage
                      difference between AIN0 to AIN2 and AIN3. No
                      single-ended channels.

SINGLE_ENDED_AND_DIFFERENTIAL -- two single ended channels reporting
                                 voltage at AIN0 and AIN1 and one
                                 differential channel reporting the
                                 voltage difference between AIN2 and
                                 AIN3.

TWO_DIFFERENTIAL -- two differential channels, the first reporting the
                    voltage difference between AIN0 and AIN1, and the
                    second reporting the voltage difference between
                    AIN2 and AIN3. No single-ended channels.

(See the documentation for the PCF8591 class for additional, optional
constructor parameters.)

For example:

    with I2CMaster() as i2c:
        adc = PCF8591(i2c, SINGLE_ENDED_AND_DIFFERENTIAL)
        
        assert adc.single_ended_input_count == 2
        assert adc.differential_input_count == 1


Once created you can use the channels of the PCF8591.  Input channels
are obtained from the `single_ended_input` and `differential_input`
methods.

    input = adc.single_ended_input(0)
    dinput = adc.differential_input(0)

The analogue signal of a channel is obtained by querying its `value`
property.  For single-ended channels the value varies between 0 and 1.
For differential channels the value varies between -0.5 and 0.5,
because the PCF8591 chip can only detect voltage differences of half
that between its reference voltage and ground.

The output channel must be opened before use, to turn on the chip's
D/A converter, and closed when no longer required, to turn it off
again and conserve power. It's easiest to do this with a context
manager.  When turned on, assigning a value between 0 and 1 to the
output channel's `value` property with set the voltage at the chip's
physical AOUT pin:

    with adc.output as output:
        # the D/A converter in the chip is now turned on
        output.value = 0.75
   
    # at the end of the with statement the D/A converter is turned off again


"""

from quick2wire.i2c import writing_bytes, reading
from quick2wire.gpio import Out, In

BASE_ADDRESS = 0x48

FOUR_SINGLE_ENDED = 0
THREE_DIFFERENTIAL = 1
SINGLE_ENDED_AND_DIFFERENTIAL = 2
TWO_DIFFERENTIAL = 3

_ANALOGUE_OUTPUT_ENABLE_FLAG = 1 << 6



class PCF8591(object):
    """API to query and control an PCF8591 A/D and D/A converter via I2C.
    
    See module documentation for details on how to use this class.
    """
    
    def __init__(self, master, mode, address=BASE_ADDRESS):
        """Initialises a PCF8591.
        
        Parameters:
        master -- the I2CMaster with which to communicate with the
                  PCF8591 chip.
        mode -- one of FOUR_SINGLE_ENDED, TWO_DIFFERENTIAL, 
                THREE_DIFFERENTIAL or SINGLE_ENDED_AND_DIFFERENTIAL.
        address -- the I2C address of the PCF8591 chip.
                   (optional, default = BASE_ADDRESS)
        """
        self.master = master
        self.address = address
        self._control_flags = (mode << 4)
        self._last_channel_read = None
        self._output = _OutputChannel(self)
        
        if mode == FOUR_SINGLE_ENDED:
            self._single_ended_inputs = tuple(self._create_single_ended_channel(i) for i in range(4))
            self._differential_inputs = ()
        elif mode == TWO_DIFFERENTIAL:
            self._single_ended_inputs = ()
            self._differential_inputs = tuple(self._create_differential_channel(i) for i in range(2))
        elif mode == SINGLE_ENDED_AND_DIFFERENTIAL:
            self._single_ended_inputs = tuple(self._create_single_ended_channel(i) for i in (0,1))
            self._differential_inputs = (self._create_differential_channel(2),)
        elif mode == THREE_DIFFERENTIAL:
            self._single_ended_inputs = ()
            self._differential_inputs = tuple(self._create_differential_channel(i) for i in range(3))
        else:
            raise ValueError("invalid mode " + str(mode))
    
    def _create_single_ended_channel(self, i):
        return _InputChannel(self, i, self.read_single_ended, 255.0)
    
    def _create_differential_channel(self, i):
        return _InputChannel(self, i, self.read_differential, 256.0)
    
    @property
    def output(self):
        """The single analogue output channel"""
        return self._output
    
    @property
    def single_ended_input_count(self):
        """The number of single-ended analogue input channels"""
        return len(self._single_ended_inputs)
    
    def single_ended_input(self, n):
        """Returns the n'th single-ended analogue input channel"""        
        return self._single_ended_inputs[n]
    
    @property
    def differential_input_count(self):
        """The number of differential analogue input channels"""
        return len(self._differential_inputs)
    
    def differential_input(self, n):
        """Returns the n'th differential analogue input channel"""        
        return self._differential_inputs[n]
    
    def enable_output(self):
        self._control_flags |= _ANALOGUE_OUTPUT_ENABLE_FLAG
        self._write_control_flags()
    
    def disable_output(self):
        self._control_flags &= ~_ANALOGUE_OUTPUT_ENABLE_FLAG
        self._write_control_flags()
    
    def _write_control_flags(self):
        if self._last_channel_read is None:
            self._last_channel_read = 0
        
        self.master.transaction(
            writing_bytes(self.address, self._control_flags|self._last_channel_read))
    
    def write(self, value):
        self.write_raw(min(max(0, int(value*255)), 0xFF))
        
    def write_raw(self, int_value):
        if self._last_channel_read is None:
            self._last_channel_read = 0
        
        self.master.transaction(
            writing_bytes(self.address, self._control_flags|self._last_channel_read, int_value))
    
    def read_single_ended(self, channel):
        """Read the 8-bit value of a single-ended input channel."""
        return self.read_raw(channel)
    
    def read_differential(self, channel):
        """Read the 8-bit value of a differential input channel."""
        unsigned = self.read_raw(channel)
        return (unsigned & 127) - (unsigned & 128)
    
    def read_raw(self, channel):
        if channel != self._last_channel_read:
            self.master.transaction(writing_bytes(self.address, self._control_flags|channel),
                                    reading(self.address, 2))
            self._last_channel_read = channel
        
        results = self.master.transaction(
            reading(self.address, 2))
        return results[0][-1]


class _OutputChannel(object):
    def __init__(self, bank):
        self.bank = bank
        self._value = 0x80
    
    def open(self):
        self.bank.enable_output()
    
    def close(self):
        self.bank.disable_output()
    
    def __enter__(self):
        self.open()
        return self
    
    def __exit__(self, *exc):
        self.close()
        return False
    
    @property
    def direction(self):
        return Out
    
    def get(self):
        return self._value
    
    def set(self, value):
        self._value = value
        self.bank.write(self._value)
    
    value = property(get, set)


class _InputChannel(object):
    def __init__(self, bank, index, read_fn, scale):
        self.bank = bank
        self.index = index
        self._read = read_fn
        self._scale = scale
    
    @property
    def direction(self):
        return In
    
    def get(self):
        return self.get_raw() / self._scale
    
    value = property(get)
    
    def get_raw(self):
        return self._read(self.index)
    
    raw_value = property(get_raw)
    
    # No-op implementations of Pin resource management API
    
    def open(self):
        pass
    
    def close(self):
        pass
    
    def __enter__(self):
        return self
    
    def __exit__(self, *exc):
        return False

