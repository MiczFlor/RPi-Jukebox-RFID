import pytest

from mock import Mock, patch
import mock

from ..GPIODevices.shutdown_button import ShutdownButton, GPIO

mock_time = Mock()

mocked_function = Mock()


@pytest.fixture
def shutdown_button():
    mocked_function.reset_mock()
    return ShutdownButton(pin=1, action=mocked_function)


class TestShutDownButton():
    def test_init(self):
        ShutdownButton(pin=1)

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
