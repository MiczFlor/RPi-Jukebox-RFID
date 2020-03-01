"""
Low-level register access and a high-level application-programming
interface for the MCP23017 I2C GPIO expander.
"""

from quick2wire.i2c import writing_bytes, reading
import quick2wire.parts.mcp23x17 as mcp23x17
from quick2wire.parts.mcp23x17 import deferred_read, immediate_read, deferred_write, immediate_write, In, Out

class MCP23017(mcp23x17.PinBanks):
    """Application programming interface to the MCP23017 GPIO extender"""
    
    def __init__(self, master, address=0x20):
        """Initialise to control an MCP23017 at the specified address via the given I2CMaster.
        
        Parameters:
        master  -- the quick2wire.i2c.I2CMaster used to communicate with the chip.
        address -- the address of the chip on the I2C bus (defaults to 0x20).
        """
        super().__init__(Registers(master, address))
        

class Registers(mcp23x17.Registers):
    """Low level access to the MCP23017 registers

    The MCP23017 has two register addressing modes, depending on the
    value of bit7 of IOCON. We assume bank=0 addressing (which is the
    POR default value).
    """
    
    def __init__(self, master, address):
        """Initialise to control an MCP23017 at the specified address via the given I2CMaster.
        
        Parameters:
        master  -- the quick2wire.i2c.I2CMaster used to communicate with the chip.
        address -- the address of the chip on the I2C bus (defaults to 0x20).
        """
        self.master = master
        self.address = address
        
    def write_register(self, register_id, byte):
        """Write the value of a register.
        
        Parameters:
        reg   -- the register address
        value -- the new value of the register
        """
        self.master.transaction(
            writing_bytes(self.address, register_id, byte))
    
    def read_register(self, register_id):
        """Read the value of a register.
        
        Parameters:
        reg   -- the register address
        
        Returns: the value of the register.
        """
        return self.master.transaction(
            writing_bytes(self.address, register_id),
            reading(self.address, 1))[0][0]


