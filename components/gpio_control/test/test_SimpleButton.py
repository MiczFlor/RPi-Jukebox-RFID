from mock import patch, MagicMock
import pytest

import RPi.GPIO as GPIO
from ..GPIODevices.simple_button import SimpleButton

pin = 1
mockedAction = MagicMock()


@pytest.fixture
def simple_button():
    return SimpleButton(pin, action=mockedAction, name='TestButton',
                        bouncetime=500, edge=GPIO.FALLING)


class TestButton:
    mockedFunction = MagicMock()

    def test_init(self):
        SimpleButton(pin, action=self.mockedFunction, name='TestButton',
                     bouncetime=500, edge=GPIO.FALLING)

    def test_callback(self, simple_button):
        simple_button.callbackFunctionHandler()(simple_button.pin)
        mockedAction.asser_called_once()

    def test_change_when_pressed(self, simple_button):
        mockedAction.asser_called_once()
        newMockedAction = MagicMock()
        simple_button.when_pressed = newMockedAction
        simple_button.callbackFunctionHandler()(simple_button.pin)
        newMockedAction.asser_called_once()
        mockedAction.asser_called_once()

    def test_hold(self, simple_button):
        GPIO.LOW = 0
        GPIO.input.side_effect = [False, False, False, True]
        simple_button.hold_time = 0
        simple_button.hold_repeat = True
        calls = mockedAction.call_count
        simple_button.callbackFunctionHandler(simple_button.pin)
        assert mockedAction.call_count - calls == 4
