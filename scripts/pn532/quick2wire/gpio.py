"""A convenient API to access the GPIO pins of the Raspberry Pi.

"""

import os
import subprocess
from contextlib import contextmanager
from quick2wire.board_revision import revision
from quick2wire.selector import EDGE


def gpio_admin(subcommand, pin, pull=None):
    if pull:
        subprocess.check_call(["gpio-admin", subcommand, str(pin), pull])
    else:
        subprocess.check_call(["gpio-admin", subcommand, str(pin)])


Out = "out"
In = "in"
    
Rising = "rising"
Falling = "falling"
Both = "both"
    
PullDown = "pulldown"
PullUp = "pullup"



class PinAPI(object):
    def __init__(self, bank, index):
        self._bank = bank
        self._index = index
    
    @property
    def index(self):
        return self._index
    
    @property
    def bank(self):
        return self._bank
    
    def __enter__(self):
        self.open()
        return self
    
    def __exit__(self, exc_type, exc_value, traceback):
        self.close()
    
    value = property(lambda p: p.get(), 
                     lambda p,v: p.set(v), 
                     doc="""The value of the pin: 1 if the pin is high, 0 if the pin is low.""")
    

class PinBankAPI(object):
    def __getitem__(self, n):
        if 0 < n < len(self):
            raise ValueError("no pin index {n} out of range", n=n)
        return self.pin(n)
    
    def write(self):
        pass
    
    def read(self):
        pass



class Pin(PinAPI):
    """Controls a GPIO pin."""
    
    __trigger__ = EDGE
    
    def __init__(self, bank, index, soc_pin_number, direction=In, interrupt=None, pull=None):
        """Creates a pin
        
        Parameters:
        user_pin_number -- the identity of the pin used to create the derived class.
        soc_pin_number  -- the pin on the header to control, identified by the SoC pin number.
        direction       -- (optional) the direction of the pin, either In or Out.
        interrupt       -- (optional)
        pull            -- (optional)
        
        Raises:
        IOError        -- could not export the pin (if direction is given)
        """
        super(Pin,self).__init__(None, index)
        self._soc_pin_number = soc_pin_number
        self._file = None
        self._direction = direction
        self._interrupt = interrupt
        self._pull = pull
    
    
    @property
    def soc_pin_number(self):
        return self._soc_pin_number
    
    def open(self):
        gpio_admin("export", self.soc_pin_number, self._pull)
        self._file = open(self._pin_path("value"), "r+")
        self._write("direction", self._direction)
        if self._direction == In:
            self._write("edge", self._interrupt if self._interrupt is not None else "none")
            
    def close(self):
        if not self.closed:
            if self.direction == Out:
                self.value = 0
            self._file.close()
            self._file = None
            self._write("direction", In)
            self._write("edge", "none")
            gpio_admin("unexport", self.soc_pin_number)
    
    def get(self):
        """The current value of the pin: 1 if the pin is high or 0 if the pin is low.
        
        The value can only be set if the pin's direction is Out.
        
        Raises: 
        IOError -- could not read or write the pin's value.
        """
        self._check_open()
        self._file.seek(0)
        v = self._file.read()
        return int(v) if v else 0
    
    def set(self, new_value):
        self._check_open()
        if self._direction != Out:
            raise ValueError("not an output pin")
        self._file.seek(0)
        self._file.write(str(int(new_value)))
        self._file.flush()
    
    @property
    def direction(self):
        """The direction of the pin: either In or Out.
        
        The value of the pin can only be set if its direction is Out.
        
        Raises:
        IOError -- could not set the pin's direction.
        """
        return self._direction
    
    @direction.setter
    def direction(self, new_value):
        self._write("direction", new_value)
        self._direction = new_value
    
    @property 
    def interrupt(self):
        """The interrupt property specifies what event (if any) will raise an interrupt.
        
        One of: 
        Rising  -- voltage changing from low to high
        Falling -- voltage changing from high to low
        Both    -- voltage changing in either direction
        None    -- interrupts are not raised
        
        Raises:
        IOError -- could not read or set the pin's interrupt trigger
        """
        return self._interrupt
    
    @interrupt.setter
    def interrupt(self, new_value):
        self._write("edge", new_value)
        self._interrupt = new_value

    @property
    def pull(self):
        return self._pull
    
    def fileno(self):
        """Return the underlying file descriptor.  Useful for select, epoll, etc."""
        return self._file.fileno()
    
    @property
    def closed(self):
        """Returns if this pin is closed"""
        return self._file is None or self._file.closed
    
    def _check_open(self):
        if self.closed:
            raise IOError(str(self) + " is closed")
    
    def _write(self, filename, value):
        with open(self._pin_path(filename), "w+") as f:
            f.write(value)
    
    def _pin_path(self, filename=""):
        return "/sys/devices/virtual/gpio/gpio%i/%s" % (self.soc_pin_number, filename)
    
    def __repr__(self):
        return self.__module__ + "." + str(self)
    
    def __str__(self):
        return "{type}({index})".format(
            type=self.__class__.__name__, 
            index=self.index)





class PinBank(PinBankAPI):
    def __init__(self, index_to_soc_fn, count=None):
        super(PinBank,self).__init__()
        self._index_to_soc = index_to_soc_fn
        self._count = count
    
    def pin(self, index, *args, **kwargs):
        return Pin(self, index, self._index_to_soc(index), *args, **kwargs)
    
    @property
    def has_len(self):
        return self._count is not None
    
    def __len__(self):
        if self._count is not None:
            return self._count
        else:
            raise TypeError(self.__class__.__name__ + " has no len")


BUTTON = 0
LED = 1
SPI_INTERRUPT = 6
I2C_INTERRUPT = 7


_pi_revision = revision()

if _pi_revision == 0:
    # Not running on the Raspberry Pi, so define no-op pin banks
    pins = PinBank(lambda p: p)
    pi_broadcom_soc = pins
    pi_header_1 = pins

else:
    def by_revision(d):
        return d[_pi_revision]


    # Maps header pin numbers to SoC GPIO numbers
    # See http://elinux.org/RPi_Low-level_peripherals
    #
    # Note: - header pins are numbered from 1, SoC GPIO from zero 
    #       - the Pi documentation identifies some header pins as GPIO0,
    #         GPIO1, etc., but these are not the same as the SoC GPIO
    #         numbers.
    
    _pi_header_1_pins = {
        3:  by_revision({1:0, 2:2}), 
        5:  by_revision({1:1, 2:3}), 
        7:  4, 
        8:  14, 
        10: 15, 
        11: 17, 
        12: 18, 
        13: by_revision({1:21, 2:27}), 
        15: 22, 
        16: 23, 
        18: 24, 
        19: 10, 
        21: 9, 
        22: 25, 
        23: 11, 
        24: 8,
        26: 7
        }
    
    _pi_gpio_pins = [_pi_header_1_pins[i] for i in [11, 12, 13, 15, 16, 18, 22, 7]]
    
    
    def lookup(pin_mapping, i):
        try:
            if i >= 0:
                return pin_mapping[i]
        except LookupError:
            pass
        
        raise IndexError(str(i) + " is not a valid pin index")

    def map_with(pin_mapping):
        return lambda i: lookup(pin_mapping,i)
    
    
    pi_broadcom_soc = PinBank(lambda p: p)
    pi_header_1 = PinBank(map_with(_pi_header_1_pins))
    pins = PinBank(map_with(_pi_gpio_pins), len(_pi_gpio_pins))
    

