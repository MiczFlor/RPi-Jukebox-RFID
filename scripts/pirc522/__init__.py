__version__ = "2.2.1"

try:
    from .rfid import RFID
    from .util import RFIDUtil
except RuntimeError:
    print("Must be used on Raspberry Pi")
