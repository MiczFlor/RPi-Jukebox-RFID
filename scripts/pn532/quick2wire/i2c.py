
import sys
from contextlib import closing
import posix
from fcntl import ioctl
from quick2wire.i2c_ctypes import *
from ctypes import create_string_buffer, sizeof, c_int, byref, pointer, addressof, string_at
from quick2wire.board_revision import revision

assert sys.version_info.major >= 3, __name__ + " is only supported on Python 3"


default_bus = 1 if revision() > 1 else 0

class I2CMaster(object):
    """Performs I2C I/O transactions on an I2C bus.
    
    Transactions are performed by passing one or more I2C I/O messages
    to the transaction method of the I2CMaster.  I2C I/O messages are
    created with the reading, reading_into, writing and writing_bytes
    functions defined in the quick2wire.i2c module.
    
    An I2CMaster acts as a context manager, allowing it to be used in a
    with statement.  The I2CMaster's file descriptor is closed at
    the end of the with statement and the instance cannot be used for
    further I/O.
    
    For example:
    
        from quick2wire.i2c import I2CMaster, writing
        
        with I2CMaster() as i2c:
            i2c.transaction(
                writing(0x20, bytes([0x01, 0xFF])))
    """
    
    def __init__(self, n=default_bus, extra_open_flags=0):
        """Opens the bus device.
        
        Arguments:
        n                -- the number of the bus (default is
                            the bus on the Raspberry Pi accessible
                            via the header pins).
        extra_open_flags -- extra flags passed to posix.open when 
                            opening the I2C bus device file (default 0; 
                            e.g. no extra flags).
        """
        self.fd = posix.open("/dev/i2c-%i"%n, posix.O_RDWR|extra_open_flags)
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_value, traceback):
        self.close()
    
    def close(self):
        """
        Closes the I2C bus device.
        """
        posix.close(self.fd)
    
    def transaction(self, *msgs):
        """
        Perform an I2C I/O transaction.

        Arguments:
        *msgs -- I2C messages created by one of the reading, reading_into,
                 writing or writing_bytes functions.
        
        Returns: a list of byte sequences, one for each read operation 
                 performed.
        """
        
        msg_count = len(msgs)
        msg_array = (i2c_msg*msg_count)(*msgs)
        ioctl_arg = i2c_rdwr_ioctl_data(msgs=msg_array, nmsgs=msg_count)
        
        ioctl(self.fd, I2C_RDWR, ioctl_arg)
        
        return [i2c_msg_to_bytes(m) for m in msgs if (m.flags & I2C_M_RD)]



def reading(addr, n_bytes):
    """An I2C I/O message that reads n_bytes bytes of data"""
    return reading_into(addr, create_string_buffer(n_bytes))

def reading_into(addr, buf):
    """An I2C I/O message that reads into an existing ctypes string buffer."""
    return _new_i2c_msg(addr, I2C_M_RD, buf)

def writing_bytes(addr, *bytes):
    """An I2C I/O message that writes one or more bytes of data. 
    
    Each byte is passed as an argument to this function.
    """
    return writing(addr, bytes)

def writing(addr, byte_seq):
    """An I2C I/O message that writes one or more bytes of data.
    
    The bytes are passed to this function as a sequence.
    """
    buf = bytes(byte_seq)
    return _new_i2c_msg(addr, 0, create_string_buffer(buf, len(buf)))


def _new_i2c_msg(addr, flags, buf):
    return i2c_msg(addr=addr, flags=flags, len=sizeof(buf), buf=buf)


def i2c_msg_to_bytes(m):
    return string_at(m.buf, m.len)
