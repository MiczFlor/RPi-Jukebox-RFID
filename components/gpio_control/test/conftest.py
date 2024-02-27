import sys
import os
from mock import MagicMock, patch
# add absolute parent path, to harmonize imports with gpio_control.py __main__ usage for tests
sys.path.insert(1, "/".join(os.path.abspath(__file__).split("/")[0:-2]))

MockRPi = MagicMock()
modules = {
    "RPi": MockRPi,
    "RPi.GPIO": MockRPi.GPIO,
}

MockRPi.GPIO.RISING = 31
MockRPi.GPIO.FALLING = 32
MockRPi.GPIO.BOTH = 33
MockRPi.GPIO.HIGH = 1
MockRPi.GPIO.LOW = 0
patcher = patch.dict("sys.modules", modules)
patcher.start()
