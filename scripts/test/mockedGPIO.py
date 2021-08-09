from mock import MagicMock, patch

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
import RPi.GPIO
GPIO = RPi.GPIO
