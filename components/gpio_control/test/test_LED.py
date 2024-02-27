import pytest
from mock import patch, call
from GPIODevices.led import LED, StatusLED, GPIO


@pytest.fixture
def led_control():
    GPIO.reset_mock()
    return LED(pin=1, initial_value=True, name='TestLED')


class TestLED:

    def test_led_init_default(self):
        GPIO.reset_mock()
        _led = LED(pin=1)
        assert _led.pin == 1
        assert _led.initial_value is True
        assert _led.name == 'LED'
        GPIO.setup.assert_called_once_with(1, GPIO.OUT)
        GPIO.output.assert_called_once_with(1, True)

    def test_led_init(self):
        GPIO.reset_mock()
        _led = LED(pin=2, initial_value=False, name='TestLED')
        assert _led.pin == 2
        assert _led.initial_value is False
        assert _led.name == 'TestLED'
        GPIO.setup.assert_called_once_with(2, GPIO.OUT)
        GPIO.output.assert_called_once_with(2, False)

    def test_led_on(self, led_control):
        GPIO.reset_mock()
        led_control.on()
        GPIO.output.assert_called_once_with(1, GPIO.HIGH)

    def test_led_off(self, led_control):
        GPIO.reset_mock()
        led_control.off()
        GPIO.output.assert_called_once_with(1, GPIO.LOW)

    def test_led_status(self, led_control):
        GPIO.reset_mock()
        GPIO.input.side_effect = [1]
        _status = led_control.status()
        assert _status == 1

    def test_statusled_init_default(self):
        GPIO.reset_mock()
        with patch('GPIODevices.led.system') as mock_system:
            with patch('time.sleep'):
                mock_system.side_effect = [False]
                _led = StatusLED(pin=1)
                assert _led.pin == 1
                assert _led.initial_value is False
                assert _led.name == 'StatusLED'
                mock_system.assert_called_with('systemctl is-active --quiet phoniebox-startup-scripts.service')
                GPIO.setup.assert_called_once_with(1, GPIO.OUT)
                GPIO.output.assert_has_calls([call(1, False), call(1, GPIO.HIGH)])

    def test_statusled_init(self):
        GPIO.reset_mock()
        with patch('GPIODevices.led.system') as mock_system:
            with patch('time.sleep'):
                mock_system.side_effect = [True, False, False]
                _led = StatusLED(pin=2, name='TestStatusLED')
                assert _led.pin == 2
                assert _led.initial_value is False
                assert _led.name == 'TestStatusLED'
                mock_system.assert_called_with('systemctl is-active --quiet phoniebox-startup-scripts.service')
                GPIO.setup.assert_called_once_with(2, GPIO.OUT)
                GPIO.output.assert_has_calls([call(2, False), call(2, GPIO.HIGH)])
