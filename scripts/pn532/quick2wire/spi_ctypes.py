# Warning: not part of the published Quick2Wire API.
#
# User space versions of kernel symbols for SPI clocking modes,
# matching <linux/spi/spi.h>
# 
# Ported to Python ctypes from <linux/spi/spidev.h>

from ctypes import *
from quick2wire.asm_generic_ioctl import _IOR, _IOW, _IOC_SIZEBITS

SPI_CPHA = 0x01
SPI_CPOL = 0x02

SPI_MODE_0 = 0
SPI_MODE_1 = SPI_CPHA
SPI_MODE_2 = SPI_CPOL
SPI_MODE_3 = SPI_CPOL|SPI_CPHA

SPI_CS_HIGH = 0x04
SPI_LSB_FIRST = 0x08
SPI_3WIRE = 0x10
SPI_LOOP = 0x20
SPI_NO_CS = 0x40
SPI_READY = 0x80


# IOCTL commands */

SPI_IOC_MAGIC = 107 # ord('k')


# struct spi_ioc_transfer - describes a single SPI transfer
#
# tx_buf:        Holds pointer to userspace buffer with transmit data, or null.
#                If no data is provided, zeroes are shifted out.
# rx_buf:        Holds pointer to userspace buffer for receive data, or null.
# len:           Length of tx and rx buffers, in bytes.
# speed_hz:      Temporary override of the device's bitrate.
# bits_per_word: Temporary override of the device's wordsize.
# delay_usecs:   If nonzero, how long to delay after the last bit transfer
#	         before optionally deselecting the device before the next transfer.
# cs_change:     True to deselect device before starting the next transfer.
#
# This structure is mapped directly to the kernel spi_transfer structure;
# the fields have the same meanings, except of course that the pointers
# are in a different address space (and may be of different sizes in some
# cases, such as 32-bit i386 userspace over a 64-bit x86_64 kernel).
# Zero-initialize the structure, including currently unused fields, to
# accomodate potential future updates.
#
# SPI_IOC_MESSAGE gives userspace the equivalent of kernel spi_sync().
# Pass it an array of related transfers, they'll execute together.
# Each transfer may be half duplex (either direction) or full duplex.
#
#	struct spi_ioc_transfer mesg[4];
#	...
#	status = ioctl(fd, SPI_IOC_MESSAGE(4), mesg);
#
# So for example one transfer might send a nine bit command (right aligned
# in a 16-bit word), the next could read a block of 8-bit data before
# terminating that command by temporarily deselecting the chip; the next
# could send a different nine bit command (re-selecting the chip), and the
# last transfer might write some register values.

class spi_ioc_transfer(Structure):
    """<linux/spi/spidev.h> struct spi_ioc_transfer"""
    
    _fields_ = [
        ("tx_buf", c_uint64),
        ("rx_buf", c_uint64),
        ("len", c_uint32),
        ("speed_hz", c_uint32),
        ("delay_usecs", c_uint16),
        ("bits_per_word", c_uint8),
        ("cs_change", c_uint8),
        ("pad", c_uint32)]
    
    __slots__ = [name for name,type in _fields_]


# not all platforms use <asm-generic/ioctl.h> or _IOC_TYPECHECK() ...
def SPI_MSGSIZE(N):
    if ((N)*(sizeof(spi_ioc_transfer))) < (1 << _IOC_SIZEBITS):
        return (N)*(sizeof(spi_ioc_transfer))
    else:
        return 0

def SPI_IOC_MESSAGE(N):
    return _IOW(SPI_IOC_MAGIC, 0, c_char*SPI_MSGSIZE(N))

# Read / Write of SPI mode (SPI_MODE_0..SPI_MODE_3)
SPI_IOC_RD_MODE =			_IOR(SPI_IOC_MAGIC, 1, c_uint8)
SPI_IOC_WR_MODE =			_IOW(SPI_IOC_MAGIC, 1, c_uint8)

# Read / Write SPI bit justification
SPI_IOC_RD_LSB_FIRST =		_IOR(SPI_IOC_MAGIC, 2, c_uint8)
SPI_IOC_WR_LSB_FIRST =		_IOW(SPI_IOC_MAGIC, 2, c_uint8)

# Read / Write SPI device word length (1..N)
SPI_IOC_RD_BITS_PER_WORD =	_IOR(SPI_IOC_MAGIC, 3, c_uint8)
SPI_IOC_WR_BITS_PER_WORD =	_IOW(SPI_IOC_MAGIC, 3, c_uint8)

# Read / Write SPI device default max speed hz
SPI_IOC_RD_MAX_SPEED_HZ =		_IOR(SPI_IOC_MAGIC, 4, c_uint32)
SPI_IOC_WR_MAX_SPEED_HZ =		_IOW(SPI_IOC_MAGIC, 4, c_uint32)

