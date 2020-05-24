import pytest
from mock import MagicMock

from ..GPIODevices.rotary_encoder import RotaryEncoder
from RPi import GPIO


pinA = 1
pinB = 2

mockCallDecr = MagicMock()
mockCallIncr = MagicMock()


@pytest.fixture
def functionCallIncr():
    return mockCallIncr


@pytest.fixture
def functionCallDecr():
    return mockCallDecr


@pytest.fixture
def rotaryEncoder(functionCallIncr, functionCallDecr):
    mockCallDecr.reset_mock()
    mockCallIncr.reset_mock()
    return RotaryEncoder(pinA, pinB,
                         functionCallIncr=functionCallIncr,
                         functionCallDecr=functionCallDecr,
                         timeBase=0.1,
                         name='MockedGPIOInteraction')


#
# @patch("RPi", autospec=True)
# @patch("RPi.GPIO", autospec=True)
class TestRotaryEncoder:

    def test_init(self, functionCallIncr, functionCallDecr):
        RotaryEncoder(pinA, pinB, functionCallIncr=functionCallIncr, functionCallDecr=functionCallDecr, timeBase=0.1,
                      name=None)

    def test_repr(self, rotaryEncoder):
        expected = "<RotaryEncoder:MockedGPIOInteraction on pin_a 1, pin_b 2,timBase 0.1 is_active=True%s>"
        assert repr(rotaryEncoder) == expected

    def test_start_stop(self, rotaryEncoder):
        calls = GPIO.add_event_detect.call_count
        assert rotaryEncoder.is_active is True
        GPIO.remove_event_detect.assert_not_called()
        rotaryEncoder.stop()
        assert GPIO.remove_event_detect.call_count == 2
        assert rotaryEncoder.is_active is False

    def test_Callback_Decr(self, rotaryEncoder):
        values = [{pinA: False, pinB: True}, {pinA: True, pinB: True}, {pinA: True, pinB: False},
                  {pinA: False, pinB: False}]
        for i in range(6):
            def side_effect(arg):
                return values[i % len(values)][arg]

            GPIO.input.side_effect = side_effect
            rotaryEncoder._Callback(1)
        mockCallDecr.assert_called_once()
        mockCallIncr.assert_not_called()

    def test_Callback_Incr(self, rotaryEncoder):
        values = [{pinA: False, pinB: True},
                  {pinA: False, pinB: False},
                  {pinA: True, pinB: False},
                  {pinA: True, pinB: True}]
        for i in range(7):
            def side_effect(arg):
                return values[i % len(values)][arg]

            GPIO.input.side_effect = side_effect
            rotaryEncoder._Callback(1)
        print(mockCallDecr.call_count, mockCallIncr.call_count)
        mockCallDecr.assert_not_called()
        mockCallIncr.assert_called_once()
