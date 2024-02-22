import pytest
from mock import MagicMock, patch
from ..GPIODevices.simple_button import SimpleButton, GPIO


mockedAction = MagicMock()


@pytest.fixture
def simple_button():
    mockedAction.reset_mock()

    return SimpleButton(pin=1, action=mockedAction, name='TestButton',
                        bouncetime=500, edge=GPIO.FALLING)


class TestButton:
    mockedFunction = MagicMock()

    def test_init(self):
        SimpleButton(pin=1, action=self.mockedFunction, name='TestButton',
                     bouncetime=500, edge=GPIO.FALLING)

    def test_antibounce(self, simple_button):
        simple_button.antibouncehack = True
        GPIO.input.side_effect = lambda *args: 1
        simple_button.callbackFunctionHandler()
        mockedAction.assert_not_called()

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
        simple_button.hold_mode = 'Repeat'
        calls = mockedAction.call_count
        simple_button.callbackFunctionHandler(simple_button.pin)
        assert mockedAction.call_count - calls == 4

    def test_repr(self):
        button = SimpleButton(name='test_repr', pin=1, edge='rising', hold_mode=None, hold_time=2.5, bouncetime=500, antibouncehack=True, pull_up_down='pull_down')
        expected = "<SimpleButton-test_repr(pin=1,edge=rising,hold_mode=None,hold_time=2.5,bouncetime=500,antibouncehack=True,pull_up_down=pull_down)>"
        assert repr(button) == expected
