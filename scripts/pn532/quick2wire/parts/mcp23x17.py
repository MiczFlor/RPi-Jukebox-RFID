"""
Low-level register access and a high-level application-programming
interface for the MCP23x17 series of GPIO expanders.

The definitions in this module are common to the I2C MCP23017 and SPI
MCP23S17. Only the methods for reading and writing to registers
differ, and they must be defined by subclassing the Registers class.
"""

import contextlib
from warnings import warn
from quick2wire.gpio import PinAPI, PinBankAPI

# TODO - import from GPIO or common definitions module
In = "in"
Out = "out"

# Bits within the IOCON regiseter
IOCON_INTPOL=1
IOCON_ODR=2
IOCON_MIRROR=6

# Register names within a bank
IODIR=0
IPOL=1
GPINTEN=2
DEFVAL=3
INTCON=4
IOCON=5
GPPU=6
INTF=7
INTCAP=8
GPIO=9
OLAT=10

bank_register_names = sorted([s for s in globals().keys() if s.upper() == s], 
                             key=lambda s: globals()[s])


BANK_SIZE = 11

_BankA = 0
_BankB = 1

def _banked_register(bank, reg):
    return reg*2 + bank

IODIRA = _banked_register(_BankA, IODIR)
IODIRB = _banked_register(_BankB, IODIR)
IPOLA = _banked_register(_BankA, IPOL)
IPOLB = _banked_register(_BankB, IPOL)
GPINTENA =_banked_register(_BankA, GPINTEN)
GPINTENB = _banked_register(_BankB, GPINTEN)
DEFVALA = _banked_register(_BankA, DEFVAL)
DEFVALB = _banked_register(_BankB, DEFVAL)
INTCONA = _banked_register(_BankA, INTCON)
INTCONB = _banked_register(_BankB, INTCON)
IOCONA = _banked_register(_BankA, IOCON)
IOCONB = _banked_register(_BankB, IOCON) # Actually addresses the same register as IOCONA
IOCON_BOTH = IOCONA
GPPUA = _banked_register(_BankA, GPPU)
GPPUB = _banked_register(_BankB, GPPU)
INTFA = _banked_register(_BankA, INTF)
INTFB = _banked_register(_BankB, INTF)
INTCAPA = _banked_register(_BankA, INTCAP)
INTCAPB = _banked_register(_BankB, INTCAP)
GPIOA = _banked_register(_BankA, GPIO)
GPIOB = _banked_register(_BankB, GPIO)
OLATA = _banked_register(_BankA, OLAT)
OLATB = _banked_register(_BankB, OLAT)

register_names = sorted([s for s in globals().keys() if s[-1] in ('A','B') and s.upper() == s], 
                        key=lambda s: globals()[s])

_initial_register_values = (
    ((IODIR,), 0xFF),
    ((IPOL, GPINTEN, DEFVAL, INTCON, GPPU, INTF, INTCAP, GPIO, OLAT), 0x00))

def _reset_sequence():
    return [(reg,value) for regs, value in _initial_register_values for reg in regs]


class Registers(object):
    """Abstract interface for reading/writing MCP23x17 registers over the I2C or SPI bus.
    
    You shouldn't normally need to use this class.

    The MCP23x17 has two register addressing modes, depending on the
    value of bit7 of IOCON. We assume bank=0 addressing (which is the
    POR default value).
    """
    
    def reset(self, iocon=0x00):
        """Reset to power-on state
        """
        self.write_register(IOCON_BOTH, iocon)
        
        for reg, value in _reset_sequence():
            self.write_banked_register(_BankA, reg, value)
            self.write_banked_register(_BankB, reg, value)
    
    def write_banked_register(self, bank, reg, value):
        """Write the value of a register within a bank.
        """
        self.write_register(_banked_register(bank, reg), value)
        
    def read_banked_register(self, bank, reg):
        """Read the value of a register within a bank.
        """
        return self.read_register(_banked_register(bank, reg))
    
    def write_register(self, reg, value):
        """Write the value of a register.
        
        Implement in subclasses.
        
        Parameters:
        reg   -- the register address
        value -- the new value of the register
        """
        pass
    
    def read_register(self, reg):
        """Read the value of a register.
        
        Implement in subclasses.
        
        Parameters:
        reg   -- the register address
        
        Returns: the value of the register.
        """
        pass



def _set_bit(current_value, bit_index, new_value):
    bit_mask = 1 << bit_index
    return (current_value | bit_mask) if new_value else (current_value & ~bit_mask)


class PinBanks(object):
    """The pin banks of an MCP23x17 chip."""
    
    def __init__(self, registers):
        self.registers = registers
        self._banks = (PinBank(self, 0), PinBank(self, 1))
    
    def __len__(self):
        """Returns the number of pin banks. (2 for the MCP23x17)"""
        return len(self._banks)
    
    def bank(self, n):
        """Returns bank n."""
        return self._banks[n]
    
    __getitem__ = bank
    
    def reset(self, interrupt_polarity=0, interrupt_open_drain=False, interrupt_mirror=True):
        """Resets the chip to power-on state and sets configuration flags in the IOCON register
        
        Parameters:
        interrupt_polarity   -- sets the polarity of the interrupt output 
                                pin: 1 = active-high. 0 = active-low.
        interrupt_open_drain -- configures the interrupt output pin as an 
                                open-drain output.
                                True = Open-drain output (overrides the 
                                interrupt_polarity).
                                False = Active driver output (the 
                                interrupt_polarity parameter sets the 
                                polarity).
        interrupt_mirror     -- Sets the interrupt output mirroring.
                                True = the interrupt output pins are 
                                internally connected.
                                False = the interrupt output pins are 
                                not connected, INTA is associated with
                                PortA and INTB is associated with PortB.
                                Should be set to True (the default) if 
                                using the Quick2Wire MCP23017 expander 
                                board.
        """
        
        self.registers.reset((interrupt_polarity << IOCON_INTPOL)
                            |(interrupt_open_drain << IOCON_ODR)
                            |(interrupt_mirror << IOCON_MIRROR))
        
        for bank in self._banks:
            bank._reset_cache()


# Read and write modes

def deferred_read(f):
    """A PinBank read mode: read() must be called explicitly."""
    pass

def immediate_read(f):
    """A PinBank read mode: read() is called automatically whenever a pin value is read.
    
    Note: this mode is not compatible with interrupts. A warning will
    be issued if interrupts are enabled on a PinBank that is in
    immediate_read mode.
    """
    f()

def deferred_write(f):
    """A PinBank write mode: write() must be called explicitly."""
    pass

def immediate_write(f):
    """A PinBank write mode: registers are written whenever Pin attributes are set."""
    f()


class PinBank(PinBankAPI):
    """A bank of 8 GPIO pins"""
    
    def __init__(self, chip, bank_id):
        self.chip = chip
        self._bank_id = bank_id
        self._pins = tuple([Pin(self, i) for i in range(8)])
        self._register_cache = [None]*BANK_SIZE # self._register_cache[IOCON] is ignored
        self._outstanding_writes = []
        self.read_mode = immediate_read
        self.write_mode = immediate_write
        self._reset_cache()
    
    @property
    def index(self):
        """The index of this bank (0 or 1)."""
        return self._bank_id
    

    def __len__(self):
        """The number of pins in the bank. (8 for the MCP23x17)"""
        return len(self._pins)
    
    
    def pin(self, n):
        """Returns pin n."""
        pin = self._pins[n]
        return pin
    
    __getitem__ = pin
    

    def read(self):
        """Read the GPIO input and interrupt capture registers from the chip.
        
        If the bank's read_mode is set to deferred_read, this must be
        called to make value property of the bank's Pins reflect the
        state of the chip's physical input pins.
        
        If the bank's read_mode is set to immediate_read, read() is
        called whenever the value property of any of the bank's Pins
        is read.
        """
        self._read_register(INTCAP)
        self._read_register(GPIO)
    

    def write(self):
        """Write changes to the pin's state capture and GPIO input registers from the chip.
        
        If the bank's write_mode is set to deferred_write, this must be
        update the chip's physical input pins so that they reflect the
        value property of the bank's Pins.
        
        If the bank's write_mode is set to immediate_write, write() is
        called whenever the value property of any of the bank's Pins
        is set.
        """
        for r in self._outstanding_writes:
            self._write_register(r, self._register_cache[r])
        self._outstanding_writes = []
    

    def _get_register_bit(self, register, bit_index):
        self.read_mode(lambda:self._read_register(register))
        
        if self._register_cache[register] is None:
            self._read_register(register)
        
        return bool(self._register_cache[register] & (1<<bit_index))
    
    
    def _read_register(self, register):
        self._register_cache[register] = self.chip.registers.read_banked_register(self._bank_id, register)
    
    
    def _set_register_bit(self, register, bit_index, new_value):
        self._register_cache[register] = _set_bit(self._register_cache[register], bit_index, new_value)
        if register not in self._outstanding_writes:
            self._outstanding_writes.append(register)
        
        self.write_mode(self.write)
    
    
    def _write_register(self, register, new_value):
        self.chip.registers.write_banked_register(self._bank_id, register, new_value)


    def _reset_cache(self):
        self._outstanding_writes = []
        for reg, value in _reset_sequence():
            self._register_cache[reg] = value
    
    
    def _check_read_mode_for_interrupts(self):
        if self.read_mode == immediate_read:
            warn("interrupts enabled when in immediate read mode", stacklevel=1)
    
    
    def __str__(self):
        return "PinBank("+self.index+")"
    

def _register_bit(register, doc, high_value=True, low_value=False):
    def _read(self):
        return high_value if self._get_register_bit(register) else low_value

    def _write(self, value):
        self._set_register_bit(register, value == high_value)
    
    return property(_read, _write, doc=doc)

class Pin(PinAPI):
    """A digital Pin that can be used for input or output."""
    
    def __init__(self, bank, index):
        """Called by the PinBank.  Not used by application code."""
        super(Pin,self).__init__(bank,index)
        self._is_claimed = False
    
    def open(self):
        """Acquire the Pin for use.
        
        Raises: ValueError if the pin is already in use.
        """
        if self._is_claimed:
            raise ValueError("pin already in use")
        self._is_claimed = True
    
    def close(self):
        self._is_claimed = False
    
    def get(self):
        """Returns the value of the pin.  
        
        The same as pin.value, but a method so that it can easily be passed around as a function.
        """
        return self._get_register_bit(GPIO)
    
    def set(self, new_value):
        """Sets the value of the pin.  
        
        The same as pin.value, but a method so that it can easily be passed around as a function.
        """
        self._set_register_bit(OLAT, new_value)
    
    direction = _register_bit(IODIR, high_value=In, low_value=Out,
                              doc="""The direction of the pin: In if the pin is used for input, Out if it is used for output.""")
    
    inverted = _register_bit(IPOL, 
        """Controls the polarity of the pin. If True, the value property will return the inverted signal on the hardware pin.""")
    
    pull_up = _register_bit(GPPU,
        """Is the pull up resistor enabled for the pin?
        True:  the pull up resistor is enabled
        False: the pull up resistor is not enabled
        """)
    
    def enable_interrupts(self, value=None):
        """Signal an interrupt on the bank's interrupt line whenever the value of the pin changes.
        
        Parameters:
        value -- If set, the interrupt is signalled when the pin's value is changed to this value.
                 If not set, the interrupt is signalled whenever the pin's value changes.
        """
        
        self.bank._check_read_mode_for_interrupts()
        if value is None:
            self._set_register_bit(INTCON, 0)
        else:
            self._set_register_bit(INTCON, 1)
            self._set_register_bit(DEFVAL, not value)
        self._set_register_bit(GPINTEN, 1)
    
    def disable_interrupts(self):
        """Do not signal an interrupt when the value of the pin changes."""
        self._set_register_bit(GPINTEN, 0)
    
    @property
    def interrupt(self):
        """Has the pin signalled an interrupt that has not been services?
        
        True:  the pin has signalled an interrupt
        False: the pin has not signalled an interrupt
        """
        return self._get_register_bit(INTCAP)
    
    def _set_register_bit(self, register, new_value):
        self.bank._set_register_bit(register, self.index, new_value)
    
    def _get_register_bit(self, register):
        return self.bank._get_register_bit(register, self.index)
        
    def __repr__(self):
        return "Pin(banks["+ str(self.bank.index) + "], " + str(self.index) + ")"

