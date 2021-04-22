import mock
import pytest
from mock import MagicMock

from ..GPIODevices import two_button_luma_oled_control
from ..GPIODevices.two_button_luma_oled_control import TwoButtonLumaOledControl

mockedFunction1 = MagicMock()
mockedFunction2 = MagicMock()

@pytest.fixture
def two_button_luma_oled_controller():
    mockedFunction1.reset_mock()
    mockedFunction2.reset_mock()

    return TwoButtonLumaOledControl(
        bcmPin1=1, bcmPin2=2,
        functionCallBtn1=mockedFunction1, functionCallBtn2=mockedFunction2,
        pull_up=True, hold_repeat=False, hold_time=0.3,
        name='TwoButtonControl'
    )

class TestTwoButtonLumaOledControl:
    def test_init(self):
        mockedFunction1 = MagicMock()
        mockedFunction2 = MagicMock()

        TwoButtonLumaOledControl(
            bcmPin1=1, bcmPin2=2,
            functionCallBtn1=mockedFunction1, functionCallBtn2=mockedFunction2,
            pull_up=True, hold_repeat=False, hold_time=0.3,
            name='TwoButtonControl'
        )

    def test_btn1_pressed(self, two_button_luma_oled_controller):
        pinA = two_button_luma_oled_controller.bcmPin1
        pinB = two_button_luma_oled_controller.bcmPin2

        two_button_luma_oled_control.GPIO.input.side_effect = lambda pin: {pinA: False, pinB: True}[pin]

        two_button_luma_oled_controller.callbackHandler()
        mockedFunction1.assert_called_once()
        mockedFunction2.assert_not_called()
        two_button_luma_oled_controller.callbackHandler()
        assert mockedFunction1.call_count == 2
        assert mockedFunction2.call_count == 0

    def test_btn2_pressed(self, two_button_luma_oled_controller):
        pinA = two_button_luma_oled_controller.bcmPin1
        pinB = two_button_luma_oled_controller.bcmPin2
        two_button_luma_oled_control.GPIO.input.side_effect = lambda pin: {pinA: True, pinB: False}[pin]
        two_button_luma_oled_controller.callbackHandler()
        mockedFunction1.assert_not_called()
        mockedFunction2.assert_called_once()
        two_button_luma_oled_controller.callbackHandler()
        assert mockedFunction1.call_count == 0
        assert mockedFunction2.call_count == 2

    def test_press_both_buttons_cycles_mode(self, two_button_luma_oled_controller):
        pinA = two_button_luma_oled_controller.bcmPin1
        pinB = two_button_luma_oled_controller.bcmPin2
        two_button_luma_oled_control.GPIO.input.side_effect = lambda pin: {pinA: False, pinB: False}[pin]

        two_button_luma_oled_controller.showSpecialInfo = MagicMock()
        two_button_luma_oled_controller.hideSpecialInfo = MagicMock()

        assert two_button_luma_oled_controller.mode == two_button_luma_oled_controller.MODE_NORMAL

        two_button_luma_oled_controller.callbackHandler()
        mockedFunction1.assert_not_called()
        mockedFunction2.assert_not_called()
        assert two_button_luma_oled_controller.mode == two_button_luma_oled_controller.MODE_CONTRAST

        two_button_luma_oled_controller.callbackHandler()
        mockedFunction1.assert_not_called()
        mockedFunction2.assert_not_called()
        two_button_luma_oled_controller.showSpecialInfo.assert_called_once()
        two_button_luma_oled_controller.hideSpecialInfo.assert_not_called()
        assert two_button_luma_oled_controller.mode == two_button_luma_oled_controller.MODE_SPECIAL_INFO

        two_button_luma_oled_controller.callbackHandler()
        mockedFunction1.assert_not_called()
        mockedFunction2.assert_not_called()
        two_button_luma_oled_controller.showSpecialInfo.assert_called_once()
        two_button_luma_oled_controller.hideSpecialInfo.assert_called_once()
        assert two_button_luma_oled_controller.mode == two_button_luma_oled_controller.MODE_NORMAL

    def test_change_contrast(self, two_button_luma_oled_controller):
        pinA = two_button_luma_oled_controller.bcmPin1
        pinB = two_button_luma_oled_controller.bcmPin2
        two_button_luma_oled_control.GPIO.input.side_effect = lambda pin: {pinA: False, pinB: False}[pin]

        two_button_luma_oled_controller.contrastUp = MagicMock()
        two_button_luma_oled_controller.contrastDown = MagicMock()

        two_button_luma_oled_controller.callbackHandler()
        mockedFunction1.assert_not_called()
        mockedFunction2.assert_not_called()

        two_button_luma_oled_control.GPIO.input.side_effect = lambda pin: {pinA: True, pinB: False}[pin]
        two_button_luma_oled_controller.callbackHandler()
        mockedFunction1.assert_not_called()
        mockedFunction2.assert_not_called()
        two_button_luma_oled_controller.contrastUp.assert_called_once()
        two_button_luma_oled_controller.contrastDown.assert_not_called()

        two_button_luma_oled_control.GPIO.input.side_effect = lambda pin: {pinA: False, pinB: True}[pin]
        two_button_luma_oled_controller.callbackHandler()
        two_button_luma_oled_controller.callbackHandler()
        mockedFunction1.assert_not_called()
        mockedFunction2.assert_not_called()
        two_button_luma_oled_controller.contrastUp.assert_called_once()
        assert two_button_luma_oled_controller.contrastDown.call_count == 2