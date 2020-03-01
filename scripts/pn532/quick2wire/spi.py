import sys
from ctypes import addressof, create_string_buffer, sizeof, string_at
import struct
import posix
from fcntl import ioctl
from quick2wire.spi_ctypes import *
from quick2wire.spi_ctypes import spi_ioc_transfer, SPI_IOC_MESSAGE

assert sys.version_info.major >= 3, __name__ + " is only supported on Python 3"


class SPIDevice:
    """Communicates with a hardware device over an SPI bus.
    
    Transactions are performed by passing one or more SPI I/O requests
    to the transaction method of the SPIDevice.  SPI I/O requests are
    created with the reading, writing, writing_bytes, duplex and
    duplex_bytes functions defined in the quick2wire.spi module.
    
    An SPIDevice acts as a context manager, allowing it to be used in
    a with statement.  The SPIDevice's file descriptor is closed at
    the end of the with statement and the instance cannot be used for
    further I/O.

    For example:
    
        from quick2wire.spi import SPIDevice, writing
        
        with SPIDevice(0) as spi0:
            spi0.transaction(
                writing(0x20, bytes([0x01, 0xFF])))
    """
    
    def __init__(self, chip_select, bus=0):
        """Opens the SPI device.
        
        Arguments:
        chip_select -- the SPI chip select line to use. The Raspberry Pi
                       only has two chip select lines, numbered 0 and 1.
        bus         -- the number of the bus (default 0, the only SPI bus
                       on the Raspberry Pi).
        """
        self.fd = posix.open("/dev/spidev%i.%i"%(bus,chip_select), posix.O_RDWR)

    def transaction(self, *transfers):
        """
        Perform an SPI I/O transaction.
        
        Arguments:
        *transfers -- SPI transfer requests created by one of the reading,
                      writing, writing_bytes, duplex or duplex_bytes 
                      functions.

        Returns: a list of byte sequences, one for each read or duplex
                 operation performed.
        """
        transfer_count = len(transfers)
        ioctl_arg = (spi_ioc_transfer*transfer_count)()

        # populate array from transfers
        for i, transfer in enumerate(transfers):
            ioctl_arg[i] = transfers[i].to_spi_ioc_transfer()

        ioctl(self.fd, SPI_IOC_MESSAGE(transfer_count), addressof(ioctl_arg))

        return [transfer.to_read_bytes() for t in transfers if t.has_read_buf]

    def close(self):
        """
        Closes the file descriptor.
        """
        posix.close(self.fd)

    @property
    def clock_mode(self):
        """
        Returns the current clock mode for the SPI bus
        """
        return ord(struct.unpack('c', ioctl(self.fd, SPI_IOC_RD_MODE, " "))[0])

    @clock_mode.setter
    def clock_mode(self,mode):
        """
        Changes the clock mode for this SPI bus

        For example:
             #start clock low, sample trailing edge
             spi.clock_mode = SPI_MODE_1
        """
        ioctl(self.fd, SPI_IOC_WR_MODE, struct.pack('I', mode))

    @property
    def speed_hz(self):
        """
        Returns the current speed in Hz for this SPI bus
        """
        return struct.unpack('I', ioctl(self.fd, SPI_IOC_RD_MAX_SPEED_HZ, "    "))[0]

    @speed_hz.setter
    def speed_hz(self,speedHz):
        """
        Changes the speed in Hz for this SPI bus
        """
        ioctl(self.fd, SPI_IOC_WR_MAX_SPEED_HZ, struct.pack('I', speedHz))

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


class _SPITransfer:
    def __init__(self, write_byte_seq = None, read_byte_count = None):
        if write_byte_seq is not None:
            self.write_bytes = bytes(write_byte_seq)
            self.write_buf = create_string_buffer(self.write_bytes, len(self.write_bytes))
        else:
            self.write_bytes = None
            self.write_buf = None
        
        if read_byte_count is not None:
            self.read_buf = create_string_buffer(read_byte_count)
        else:
            self.read_buf = None
    
    def to_spi_ioc_transfer(self):
        return spi_ioc_transfer(
            tx_buf=_safe_address_of(self.write_buf),
            rx_buf=_safe_address_of(self.read_buf),
            len=_safe_size_of(self.write_buf, self.read_buf))

    @property
    def has_read_buf(self):
        return self.read_buf is not None

    def to_read_bytes(self):
        return string_at(self.read_buf, sizeof(self.read_buf))


def _safe_size_of(write_buf, read_buf):
    if write_buf is not None and read_buf is not None:
        assert sizeof(write_buf) == sizeof(read_buf)
        return sizeof(write_buf)
    elif write_buf is not None:
        return sizeof(write_buf)
    else:
        return sizeof(read_buf)

def _safe_address_of(buf):
    return 0 if buf is None else addressof(buf)

def duplex(write_byte_sequence):
    """An SPI transfer that writes the write_byte_sequence to the device and reads len(write_byte_sequence) bytes from the device.
    
    The bytes to be written are passed to this function as a sequence.
    """
    return _SPITransfer(write_byte_seq=write_byte_sequence, read_byte_count=len(write_byte_sequence))

def duplex_bytes(*write_bytes):
    """An SPI transfer that writes the write_bytes to the device and reads len(write_bytes) bytes from the device.
    
    Each byte to be written is passed as an argument to this function.
    """
    return duplex(write_bytes)

def reading(byte_count):
    """An SPI transfer that shifts out byte_count zero bytes and reads byte_counts bytes from the device."""
    return _SPITransfer(read_byte_count=byte_count)

def writing(byte_sequence):
    """An SPI transfer that writes one or more bytes of data and ignores any bytes read from the device.
    
    The bytes are passed to this function as a sequence.
    """
    return _SPITransfer(write_byte_seq=byte_sequence)

def writing_bytes(*byte_values):
    """An SPI transfer that writes one or more bytes of data and ignores any bytes read from the device.
    
    Each byte is passed as an argument to this function.
    """
    return writing(byte_values)

