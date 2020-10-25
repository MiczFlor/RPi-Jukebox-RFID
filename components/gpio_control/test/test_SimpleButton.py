from mock import patch, MagicMock
import pytest

import RPi.GPIO as GPIO
from ..GPIODevices.simple_button import SimpleButton

pin = 1
mockedAction = MagicMock()


@pytest.fixture
def simple_button():
    mockedAction.reset_mock()

    return SimpleButton(pin, action=mockedAction, name='TestButton',
                        bouncetime=500, edge=GPIO.FALLING)


class TestButton:
    mockedFunction = MagicMock()

    def test_init(self):
        SimpleButton(pin, action=self.mockedFunction, name='TestButton',
                     bouncetime=500, edge=GPIO.FALLING)

    def test_callback(self, simple_button):
        simple_button.callbackFunctionHandler(simple_button.pin)
        mockedAction.assert_called_once_with()

    def test_callback_without_pin_argument(self, simple_button):
        simple_button.callbackFunctionHandler()
        mockedAction.assert_called_once_with()

    def test_callback_with_wrong_pin_argument(self, simple_button):
        simple_button.callbackFunctionHandler(simple_button.pin + 1)
        mockedAction.assert_called_once_with(simple_button.pin + 1)

    def test_callback_with_more_arguments(self, simple_button):
        simple_button.callbackFunctionHandler(simple_button.pin, 5)
        mockedAction.assert_called_once_with(5)

    def test_change_when_pressed(self, simple_button):
        simple_button.callbackFunctionHandler(simple_button.pin, 5)

        newMockedAction = MagicMock()
        simple_button.when_pressed = newMockedAction
        simple_button.callbackFunctionHandler(simple_button.pin)

        newMockedAction.assert_called_once_with()
        mockedAction.assert_called_once_with(5)

    def test_hold(self, simple_button):
        GPIO.LOW = 0
        GPIO.input.side_effect = [False, False, False, True]
        simple_button.hold_time = 0
        simple_button.hold_repeat = True
        calls = mockedAction.call_count
        simple_button.callbackFunctionHandler(simple_button.pin)
        assert mockedAction.call_count - calls == 4
