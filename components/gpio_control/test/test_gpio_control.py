import configparser
import logging

from mock import patch, MagicMock
from components.gpio_control.gpio_control import get_all_devices

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

mockedFunction1 = MagicMock()
mockedFunction2 = MagicMock()
mockedFunction3 = MagicMock()

mockedFunction1.side_effect = lambda *args: print('MockFunction1 called')
mockedFunction2.side_effect = lambda *args: print('MockFunction2 called')
mockedFunction3.side_effect = lambda *args: print('MockFunction3 called')

logging.basicConfig(level='DEBUG')


def testMain():
    config = configparser.ConfigParser()
    config.read('./gpio_settings_test.ini')
    devices = get_all_devices(config)
    print(devices)
    pass
