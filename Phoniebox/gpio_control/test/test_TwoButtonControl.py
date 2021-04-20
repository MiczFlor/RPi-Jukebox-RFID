import mock
import pytest
from mock import MagicMock

from ..GPIODevices import two_button_control
from ..GPIODevices.two_button_control import functionCallTwoButtons, TwoButtonControl


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
mockedFunction2 = MagicMock()
mockedFunction3 = MagicMock()


@pytest.fixture
def two_button_controller():
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

    def test_btn1_pressed(self, two_button_controller):
        pinA = two_button_controller.bcmPin1
        pinB = two_button_controller.bcmPin2

        def func(pin):
            values = {pinA: False, pinB: True}
            if pin in values:
                return values[pin]
            else:
                print('Cannot find pin {} in values: {}'.format(pin, values))
                return None
        two_button_control.GPIO.input.side_effect = func
        two_button_controller.action()
        mockedFunction1.assert_called_once()
        mockedFunction2.assert_not_called()
        mockedFunction3.assert_not_called()
        two_button_controller.action()
        assert mockedFunction1.call_count == 2

    def test_btn2_pressed(self, two_button_controller):
        pinA = two_button_controller.bcmPin1
        pinB = two_button_controller.bcmPin2
        two_button_control.GPIO.input.side_effect = lambda pin: {pinA: True, pinB: False}[pin]
        two_button_controller.action()
        mockedFunction1.assert_not_called()
        mockedFunction2.assert_called_once()
        mockedFunction3.assert_not_called()
        two_button_controller.action()
        assert mockedFunction2.call_count == 2

    def test_btn1_and_btn2_pressed(self, two_button_controller):
        pinA = two_button_controller.bcmPin1
        pinB = two_button_controller.bcmPin2
        two_button_control.GPIO.input.side_effect = lambda pin: {pinA: False, pinB: False}[pin]
        two_button_controller.action()
        mockedFunction1.assert_not_called()
        mockedFunction2.assert_not_called()
        mockedFunction3.assert_called_once()
        two_button_controller.action()
        assert mockedFunction3.call_count == 2

    def test_repr(self, two_button_controller):
        expected = "<TwoBtnControl-TwoButtonControl(1, 2,two_buttons_action=True)>"
        assert repr(two_button_controller) == expected
