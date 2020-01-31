from __future__ import unicode_literals, absolute_import, print_function, division
from gpiozero.pins.mock import MockFactory
from scripts.RotaryEncoder import RotaryEncoder, TableValues, Device, RotaryEncoderClickable

str = type('')


import sys
import pytest
from time import sleep

from gpiozero import *
from gpiozero.pins.mock import MockPWMPin, MockPin

from mock import MagicMock


@pytest.fixture
def pins_for_rotary_encoder():
    pin_a = Device.pin_factory.pin(2)
    pin_b = Device.pin_factory.pin(3)
    return pin_a, pin_b

@pytest.fixture
def pins_for_clickable_rotary_encoder(pins_for_rotary_encoder):
    pin_button = Device.pin_factory.pin(4)
    return (*pins_for_rotary_encoder, pin_button)


def teardown_module(module):
    # make sure we reset the default
    Device.pin_factory.pwm = False

class TestRotaryEncoder():
    @classmethod
    def teardown_class(cls):
        # make sure we reset the default
        Device.pin_factory.pwm = False

    def teardown_method(self, method):
        Device.pin_factory.reset()

    def setup_method(self, method):
        """ setup any state tied to the execution of the given method in a
        class.  setup_method is invoked for every test method of a class.
        """
        Device.pin_factory = MockFactory()
        Device.pin_factory.pin_class = MockPin

    def test_rotary_encoder_initialization(self):
        pin_a = Device.pin_factory.pin(17)
        pin_b = Device.pin_factory.pin(27)

        with RotaryEncoder(17, 27, pull_up=True) as encoder:
            assert not encoder.closed
            assert encoder.is_active

            assert encoder.pin_a.pin is pin_a
            assert encoder.pin_b.pin is pin_b

            assert encoder.pin_a.pull_up
            assert encoder.pin_b.pull_up

        assert encoder.closed
        assert not encoder.is_active

    def test_rotary_encoder_close(self):
        pin_a = Device.pin_factory.pin(17)
        pin_b = Device.pin_factory.pin(27)

        with RotaryEncoder(17, 27, pull_up=True) as encoder:
            assert not encoder.closed
            assert encoder.is_active

            encoder.close()

            assert encoder.closed
            assert not encoder.is_active

        encoder = RotaryEncoder(17, 27, pull_up=False)
        assert not encoder.closed
        assert encoder.is_active

        encoder.close()

    def test_rotary_encoder_repr(self, pins_for_rotary_encoder):

        with RotaryEncoder(2, 3, pull_up=True) as encoder:
            assert repr(
                encoder) == '<gpiozero.RotaryEncoder object on pin_a GPIO2, pin_b GPIO3, pull_up=True, is_active=True>'

    def test_rotary_encoder_table_values(self):
        assert TableValues.calculate_index(True, False, False, False) == 8
        assert TableValues.calculate_index(False, True, False, False) == 4
        assert TableValues.calculate_index(False, False, True, False) == 2
        assert TableValues.calculate_index(False, False, False, True) == 1

        assert TableValues.calculate_index(True, True, True, True) == 15

    def test_rotary_encoder_rotate_clockwise(self,pins_for_rotary_encoder):
        pin_a, pin_b = pins_for_rotary_encoder
        with RotaryEncoder(2, 3) as encoder:
            pin_a.drive_low()
            pin_b.drive_high()

            encoder.when_rotated = MagicMock()

            pin_a.drive_high()

            encoder.when_rotated.assert_called_with(1)

    def test_rotary_encoder_rotate_counter_clockwise(self,pins_for_rotary_encoder):
        pin_a, pin_b = pins_for_rotary_encoder

        with RotaryEncoder(2, 3) as encoder:
            pin_a.drive_low()
            pin_b.drive_high()

            encoder.when_rotated = MagicMock()

            pin_b.drive_low()

            encoder.when_rotated.assert_called_with(-1)

    def test_rotary_encoder_value_not_defined(self,pins_for_rotary_encoder):
        with RotaryEncoder(2, 3) as encoder:
            assert encoder.value is None

    def test_rotary_encoder_clickable(self):
        pin_a = Device.pin_factory.pin(17)
        pin_b = Device.pin_factory.pin(27)
        pin_button = Device.pin_factory.pin(4)

        with RotaryEncoderClickable(17, 27, 4, encoder_pull_up=True, button_pull_up=True) as encoder:
            assert not encoder.closed
            assert encoder.is_active

            assert encoder.rotary_encoder.pin_a.pin is pin_a
            assert encoder.rotary_encoder.pin_b.pin is pin_b
            assert encoder.button.pin is pin_button

            assert encoder.rotary_encoder.pin_a.pull_up
            assert encoder.rotary_encoder.pin_b.pull_up
            assert encoder.button.pull_up

        assert encoder.closed
        assert not encoder.is_active

        with RotaryEncoderClickable(17, 27, 4, encoder_pull_up=False, button_pull_up=False) as encoder:
            assert not encoder.closed
            assert encoder.is_active

            assert encoder.rotary_encoder.pin_a.pin is pin_a
            assert encoder.rotary_encoder.pin_b.pin is pin_b
            assert encoder.button.pin is pin_button

            assert not encoder.rotary_encoder.pin_a.pull_up
            assert not encoder.rotary_encoder.pin_b.pull_up
            assert not encoder.button.pull_up

        assert encoder.closed
        assert not encoder.is_active

    def test_rotary_encoder_clickable_value(self, pins_for_clickable_rotary_encoder):
        pin_a, pin_b, pin_button = pins_for_clickable_rotary_encoder

        with RotaryEncoderClickable(2, 3, 4) as encoder:
            pin_button.drive_low()
            assert encoder.value is None

            pin_button.drive_high()
            assert encoder.value is None


    def test_rotary_encoder_clickable_repr(self, pins_for_clickable_rotary_encoder):
        with RotaryEncoderClickable(2, 3, 4) as encoder:
            assert repr(
                encoder) == '<gpiozero.RotaryEncoderClickable object on pin_a GPIO2, pin_b GPIO3, button_pin GPIO4, encoder_pull_up=True, button_pull_up=True, is_active=True>'

    def test_rotary_encoder_composite_device(self, pins_for_clickable_rotary_encoder):
        when_pressed = lambda *args: None
        when_rotated = lambda *args: None

        with RotaryEncoderClickable(2, 3, 4) as encoder:
            encoder.when_pressed = when_pressed
            assert when_pressed == encoder.when_pressed

            encoder.when_rotated = when_rotated
            assert when_rotated == encoder.when_rotated
