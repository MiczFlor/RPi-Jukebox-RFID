import configparser

import mock
from mock import patch, MagicMock

import pytest

MockRPi = MagicMock()
modules = {
    "RPi": MockRPi,
    "RPi.GPIO": MockRPi.GPIO,
}
patcher = patch.dict("sys.modules", modules)
patcher.start()

MockRPi.GPIO.RISING = 31
MockRPi.GPIO.FALLING = 32
MockRPi.GPIO.BOTH = 33
MockRPi.GPIO.HIGH = 1
MockRPi.GPIO.LOW = 0

from scripts.TwoButtonControl import functionCallTwoButtons, TwoButtonControl

from gpio_control import get_all_devices


@pytest.fixture
def btn1Mock():
    return mock.MagicMock()


@pytest.fixture
def btn2Mock():
    return mock.MagicMock()


@pytest.fixture
def functionCall1Mock():
    return mock.MagicMock()


@pytest.fixture
def functionCall2Mock():
    return mock.MagicMock()


@pytest.fixture
def functionCallBothPressedMock():
    return mock.MagicMock()


def test_functionCallTwoButtonsOnlyBtn1Pressed(btn1Mock,
                                               btn2Mock,
                                               functionCall1Mock,
                                               functionCall2Mock,
                                               functionCallBothPressedMock):
    btn1Mock.is_pressed = True
    btn2Mock.is_pressed = False
    func = functionCallTwoButtons(btn1Mock,
                                  btn2Mock,
                                  functionCall1Mock,
                                  functionCall2Mock,
                                  functionCallBothPressed=functionCallBothPressedMock)
    func()
    functionCall1Mock.assert_called_once_with()
    functionCall2Mock.assert_not_called()
    functionCallBothPressedMock.assert_not_called()


# def test_functionCallTwoButtonsOnlyBtn2Pressed(btn1Mock, btn2Mock, functionCall1Mock, functionCall2Mock,
#                                                functionCallBothPressedMock):
#     btn1Mock.is_pressed = False
#     btn2Mock.is_pressed = True
#     func = functionCallTwoButtons(btn1Mock, btn2Mock, functionCall1Mock,
#                                   functionCallBothPressed=functionCallBothPressedMock)
#     func()
#     functionCall1Mock.assert_not_called()
#     functionCall2Mock.assert_called_once_with()
#     functionCallBothPressedMock.assert_not_called()


def test_functionCallTwoButtonsBothBtnsPressedFunctionCallBothPressedExists(btn1Mock,
                                                                            btn2Mock,
                                                                            functionCall1Mock,
                                                                            functionCall2Mock,
                                                                            functionCallBothPressedMock):
    btn1Mock.is_pressed = True
    btn2Mock.is_pressed = True
    func = functionCallTwoButtons(btn1Mock, btn2Mock, functionCall1Mock, functionCall2Mock,
                                  functionCallBothPressed=functionCallBothPressedMock)
    func()
    functionCall1Mock.assert_not_called()
    functionCall2Mock.assert_not_called()
    functionCallBothPressedMock.assert_called_once_with()


def test_functionCallTwoButtonsBothBtnsPressedFunctionCallBothPressedIsNone(btn1Mock,
                                                                            btn2Mock,
                                                                            functionCall1Mock,
                                                                            functionCall2Mock):
    btn1Mock.is_pressed = True
    btn2Mock.is_pressed = True
    func = functionCallTwoButtons(btn1Mock, btn2Mock, functionCall1Mock, functionCall2Mock,
                                  functionCallBothPressed=None)
    func()
    functionCall1Mock.assert_not_called()
    functionCall2Mock.assert_not_called()


mockedFunction1 = MagicMock()
mockedFunction1.side_effect = lambda *args: print('MockFunction1 called')
mockedFunction2 = MagicMock()
mockedFunction2.side_effect = lambda *args: print('MockFunction2 called')
mockedFunction3 = MagicMock()
mockedFunction3.side_effect = lambda *args: print('MockFunction3 called')


@pytest.fixture
def two_button_control():
    mockedFunction1.reset_mock()
    mockedFunction2.reset_mock()
    mockedFunction3.reset_mock()
    return TwoButtonControl(bcmPin1=1,
                            bcmPin2=2,
                            functionCallBtn1=mockedFunction1,
                            functionCallBtn2=mockedFunction2,
                            functionCallTwoBtns=mockedFunction3,
                            pull_up=True,
                            hold_repeat=False,
                            hold_time=0.3,
                            name='TwoButtonControl')


class TestTwoButtonControl:
    def test_init(self):
        TwoButtonControl(bcmPin1=1,
                         bcmPin2=2,
                         functionCallBtn1=mockedFunction1,
                         functionCallBtn2=mockedFunction2,
                         functionCallTwoBtns=mockedFunction3,
                         pull_up=True,
                         hold_repeat=False,
                         hold_time=0.3,
                         name='TwoButtonControl')

    def test_btn1_pressed(self, two_button_control):
        pinA = two_button_control.bcmPin1
        pinB = two_button_control.bcmPin2
        MockRPi.GPIO.input.side_effect = lambda pin: {pinA: False, pinB: True}[pin]
        two_button_control.action()
        mockedFunction1.assert_called_once()
        mockedFunction2.assert_not_called()
        mockedFunction3.assert_not_called()
        two_button_control.action()
        assert mockedFunction1.call_count == 2

    def test_btn2_pressed(self, two_button_control):
        pinA = two_button_control.bcmPin1
        pinB = two_button_control.bcmPin2
        MockRPi.GPIO.input.side_effect = lambda pin: {pinA: True, pinB: False}[pin]
        two_button_control.action()
        mockedFunction1.assert_not_called()
        mockedFunction2.assert_called_once()
        mockedFunction3.assert_not_called()
        two_button_control.action()
        assert mockedFunction2.call_count == 2

    def test_btn1_and_btn2_pressed(self, two_button_control):
        pinA = two_button_control.bcmPin1
        pinB = two_button_control.bcmPin2
        MockRPi.GPIO.input.side_effect = lambda pin: {pinA: False, pinB: False}[pin]
        two_button_control.action()
        mockedFunction1.assert_not_called()
        mockedFunction2.assert_not_called()
        mockedFunction3.assert_called_once()
        two_button_control.action()
        assert mockedFunction3.call_count == 2

    def test_repr(self, two_button_control):
        expected = "<TwoBtnControl-TwoButtonControl(1, 2,two_buttons_action=True)>"
        assert repr(two_button_control) == expected


def testMain():
    config = configparser.ConfigParser()
    config.read('./gpio_settings_test.ini')
    devices = get_all_devices(config)
    print(devices)
    pass

