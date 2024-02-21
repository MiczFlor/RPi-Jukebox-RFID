import sys
import os
from mock import MagicMock, patch
sys.path.append(os.path.abspath('components/gpio_control'))

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
