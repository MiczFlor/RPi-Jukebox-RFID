import pytest
from mock import Mock, patch
from ..GPIODevices.shutdown_button import ShutdownButton, GPIO

mock_time = Mock()
mocked_function = Mock()


@pytest.fixture
def shutdown_button():
    mocked_function.reset_mock()
    return ShutdownButton(pin=1, action=mocked_function, led_pin=5)

class TestShutDownButton():

    @patch('time.sleep', mock_time)
    def test_noled(self):
        mocked_function_local = Mock()
        shutdown_button_local = ShutdownButton(pin=1, action=mocked_function_local)
        GPIO.input.side_effect = lambda *args: 0
        shutdown_button_local.callbackFunctionHandler()
        mocked_function_local.assert_called_once()

    @patch('time.sleep', mock_time)
    def test_antibounce(self, shutdown_button):
        shutdown_button.antibouncehack = True
        GPIO.input.side_effect = lambda *args: 1
        shutdown_button.callbackFunctionHandler()
        mocked_function.assert_not_called()

    @patch('time.sleep', mock_time)
    def test_action_too_short_press(self, shutdown_button):
        for i in range(9):
            GPIO.input.reset_mock()
            GPIO.input.side_effect = i * [0] + [1]
            shutdown_button.callbackFunctionHandler()
            assert GPIO.input.call_count == i + 1
            mocked_function.assert_not_called()

    @patch('time.sleep', mock_time)
    def test_action_invalid_press(self, shutdown_button):
        GPIO.input.side_effect = lambda *args: 1
        shutdown_button.callbackFunctionHandler()
        mocked_function.assert_not_called()

    @patch('time.sleep', mock_time)
    def test_action_valid_press(self, shutdown_button):
        GPIO.input.side_effect = lambda *args: 0
        shutdown_button.callbackFunctionHandler()
        mocked_function.assert_called_once()

    @patch('time.sleep', mock_time)
    def test_callback(self, shutdown_button):
        GPIO.input.side_effect = lambda *args: 0
        shutdown_button.callbackFunctionHandler(shutdown_button.pin, shutdown_button.pin)
        mocked_function.assert_called_once_with(shutdown_button.pin)

    def test_repr(self):
        button = ShutdownButton(name='test_repr', pin=1, hold_time=2.5, iteration_time=.8, led_pin=5, edge='rising', bouncetime=200, antibouncehack=True, pull_up_down='pull_down')
        expected = "<ShutdownButton-test_repr(pin=1,hold_time=2.5,iteration_time=0.8,led_pin=5,edge=rising,bouncetime=200,antibouncehack=True,pull_up_down=pull_down)>"
        assert repr(button) == expected
