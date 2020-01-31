import mock
import pytest

from scripts.gpio_contorl import functionCallTwoButtons


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


def test_functionCallTwoButtonsOnlyBtn2Pressed(btn1Mock, btn2Mock, functionCall1Mock, functionCall2Mock,
                                               functionCallBothPressedMock):
    btn1Mock.is_pressed = False
    btn2Mock.is_pressed = True
    func = functionCallTwoButtons(btn1Mock, btn2Mock, functionCall1Mock, functionCall2Mock,
                                  functionCallBothPressed=functionCallBothPressedMock)
    func()
    functionCall1Mock.assert_not_called()
    functionCall2Mock.assert_called_once_with()
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
