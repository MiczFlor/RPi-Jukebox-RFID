import pytest
from mock import patch, call
from ..gpio_control import gpio_control
from ..GPIODevices import StatusLED, LED, RotaryEncoder, SimpleButton, ShutdownButton, TwoButtonControl

import configparser

# import logging
# logging.basicConfig(level='DEBUG')


@pytest.fixture
def gpio_control_class():

    class MockFunctionCalls:

        def funcTestWithoutParameter(self, *args):
            return "funcTestWithoutParameter"

        def funcTestWithParameter(self, param1):
            return f"funcTestWithParameter({param1})"

    _gpio_control_class = gpio_control(MockFunctionCalls)  # function_calls will be mocked
    return _gpio_control_class


# Mock function 'getFunctionCall' and just return given parameter
def mock_gpio_control_getFunctionCall(self, func_name, func_args):
    return str(func_name) + '-' + str(func_args)


@patch.object(gpio_control, 'getFunctionCall', mock_gpio_control_getFunctionCall)
def func_test_generateDevice_type(gpio_control_class, name, configArray, type):
    config = configparser.ConfigParser()
    config[name] = configArray
    with patch.object(type, '__init__', return_value=None) as mock_init:
        device = gpio_control_class.generate_device(config[name], name)
        assert isinstance(device, type) is True
        return mock_init


class TestGPIOControl:

    def test_getAllDevices_empty(self, gpio_control_class):
        config = configparser.ConfigParser()
        devices = gpio_control_class.get_all_devices(config)
        assert not devices

    def test_getAllDevices_empty_device(self, gpio_control_class):
        name = 'TestDevice'
        config = configparser.ConfigParser()
        config[name] = {}
        devices = gpio_control_class.get_all_devices(config)
        assert not devices

    def test_getAllDevices_type_unknown(self, gpio_control_class):
        name = 'TestDevice'
        config = configparser.ConfigParser()
        config[name] = {'enabled': 'true'}
        with patch.object(gpio_control_class, gpio_control_class.generate_device.__name__,
                          return_value=None) as mock_generate_device:
            devices = gpio_control_class.get_all_devices(config)
            mock_generate_device.assert_called_once_with(config[name], name)
            assert not devices

    def test_getAllDevices_type_known(self, gpio_control_class):
        name = 'TestDevice'
        config = configparser.ConfigParser()
        config[name] = {'enabled': 'true'}
        with patch.object(gpio_control_class, gpio_control_class.generate_device.__name__,
                          return_value='TestDeviceResult') as mock_generate_device:
            devices = gpio_control_class.get_all_devices(config)
            mock_generate_device.assert_called_once_with(config[name], name)
            assert len(devices) == 1
            assert devices[0] == 'TestDeviceResult'

    # ---------------

    def test_generateDevice_unknown(self, gpio_control_class):
        name = 'TEST_unknown'
        config = configparser.ConfigParser()
        config[name] = {'Type': 'unknown', 'Pin': '5'}
        device = gpio_control_class.generate_device(config[name], name)
        assert device is None

    def test_generateDevice_StatusLED(self, gpio_control_class):
        name = 'TEST_StatusLED'
        configArray = {'Type': StatusLED.__name__, 'Pin': '5'}
        mock_init = func_test_generateDevice_type(gpio_control_class, name, configArray, StatusLED)
        mock_init.assert_called_once_with(5, name=name)

    def test_generateDevice_MPDStatusLED(self, gpio_control_class):
        name = 'TEST_MPDStatusLED'
        configArray = {'Type': 'MPDStatusLED', 'Pin': '5'}
        mock_init = func_test_generateDevice_type(gpio_control_class, name, configArray, StatusLED)
        mock_init.assert_called_once_with(5, name=name)

    def test_generateDevice_LED_default(self, gpio_control_class):
        name = 'TEST_LED'
        configArray = {'Type': LED.__name__, 'Pin': '5', }
        mock_init = func_test_generateDevice_type(gpio_control_class, name, configArray, LED)
        mock_init.assert_called_once_with(5, name=name, initial_value=True)

    def test_generateDevice_LED(self, gpio_control_class):
        name = 'TEST_LED'
        configArray = {'Type': 'LED', 'Pin': '5', 'initial_value': 'False'}
        mock_init = func_test_generateDevice_type(gpio_control_class, name, configArray, LED)
        mock_init.assert_called_once_with(5, name=name, initial_value=False)

    def test_generateDevice_RotaryEncoder_default(self, gpio_control_class):
        name = 'TEST_RotaryEncoder'
        configArray = {'Type': RotaryEncoder.__name__, 'Pin1': '5', 'Pin2': '6',
                        'functionCall1': 'test_funcCall1', 'functionCall2': 'test_funcCall2'}
        mock_init = func_test_generateDevice_type(gpio_control_class, name, configArray, RotaryEncoder)
        mock_init.assert_called_once_with(5, 6, "test_funcCall1-None", "test_funcCall2-None", 0.1, name=name)

    def test_generateDevice_RotaryEncoder(self, gpio_control_class):
        name = 'TEST_RotaryEncoder'
        configArray = {'Type': RotaryEncoder.__name__, 'Pin1': '5', 'Pin2': '6',
                        'functionCall1': 'test_funcCall1', 'functionCall2': 'test_funcCall2',
                        'timeBase': '1.1'}
        mock_init = func_test_generateDevice_type(gpio_control_class, name, configArray, RotaryEncoder)
        mock_init.assert_called_once_with(5, 6, "test_funcCall1-None", "test_funcCall2-None", 1.1, name=name)

    def test_generateDevice_SimpleButton_default(self, gpio_control_class):
        name = 'TEST_SimpleButton'
        configArray = {'Type': SimpleButton.__name__, 'Pin': '5',
                        'functionCall': 'test_funcCall1'}
        mock_init = func_test_generateDevice_type(gpio_control_class, name, configArray, SimpleButton)
        mock_init.assert_called_once_with(5, action="test_funcCall1-None",
                                            action2="None-None", name=name, bouncetime=500,
                                            antibouncehack=False, edge='falling', hold_mode=None,
                                            hold_time=0.3, pull_up_down='pull_up')

    def test_generateDevice_SimpleButton(self, gpio_control_class):
        name = 'TEST_SimpleButton'
        configArray = {'Type': SimpleButton.__name__, 'Pin': '5',
                        'functionCall': 'test_funcCall1', 'functionCallArgs': 'test_funcCall1Args',
                        'functionCall2': 'test_funcCall2', 'functionCall2Args': 'test_funcCall2Args',
                        'bouncetime': 299, 'antibouncehack': 'True', 'edge': 'test_edge',
                        'hold_mode': 'test_holdmode', 'hold_time': 1.3, 'pull_up_down': 'test_pull_up_down'}
        mock_init = func_test_generateDevice_type(gpio_control_class, name, configArray, SimpleButton)
        mock_init.assert_called_once_with(5, action="test_funcCall1-test_funcCall1Args",
                                            action2="test_funcCall2-test_funcCall2Args", name=name, bouncetime=299,
                                            antibouncehack=True, edge='test_edge', hold_mode='test_holdmode',
                                            hold_time=1.3, pull_up_down='test_pull_up_down')

    def test_generateDevice_Button_default(self, gpio_control_class):
        name = 'TEST_Button'
        configArray = {'Type': 'Button', 'Pin': '5',
                        'functionCall': 'test_funcCall1'}
        mock_init = func_test_generateDevice_type(gpio_control_class, name, configArray, SimpleButton)
        mock_init.assert_called_once_with(5, action="test_funcCall1-None",
                                            action2="None-None", name=name, bouncetime=500,
                                            antibouncehack=False, edge='falling', hold_mode=None,
                                            hold_time=0.3, pull_up_down='pull_up')

    def test_generateDevice_Button(self, gpio_control_class):
        name = 'TEST_Button'
        configArray = {'Type': 'Button', 'Pin': '5',
                        'functionCall': 'test_funcCall1', 'functionCallArgs': 'test_funcCall1Args',
                        'functionCall2': 'test_funcCall2', 'functionCall2Args': 'test_funcCall2Args',
                        'bouncetime': 299, 'antibouncehack': 'True', 'edge': 'test_edge',
                        'hold_mode': 'test_holdmode', 'hold_time': 1.3, 'pull_up_down': 'test_pull_up_down'}
        mock_init = func_test_generateDevice_type(gpio_control_class, name, configArray, SimpleButton)
        mock_init.assert_called_once_with(5, action="test_funcCall1-test_funcCall1Args",
                                            action2="test_funcCall2-test_funcCall2Args", name=name, bouncetime=299,
                                            antibouncehack=True, edge='test_edge', hold_mode='test_holdmode',
                                            hold_time=1.3, pull_up_down='test_pull_up_down')

    def test_generateDevice_ShutdownButton_default(self, gpio_control_class):
        name = 'TEST_ShutdownButton'
        configArray = {'Type': ShutdownButton.__name__, 'Pin': '5'}
        mock_init = func_test_generateDevice_type(gpio_control_class, name, configArray, ShutdownButton)
        mock_init.assert_called_once_with(pin=5, action="functionCallShutdown-None",
                                          name=name, bouncetime=500, antibouncehack=False, edge='falling',
                                          hold_time=3.0, iteration_time=0.2, led_pin=None,
                                          pull_up_down='pull_up')

    def test_generateDevice_ShutdownButton(self, gpio_control_class):
        name = 'TEST_ShutdownButton'
        configArray = {'Type': ShutdownButton.__name__, 'Pin': '5',
                        'functionCall': 'test_funcCall1', 'functionCallArgs': 'test_funcCall1Args',
                        'bouncetime': 299, 'antibouncehack': 'True', 'edge': 'test_edge',
                        'hold_time': 1.3, 'iteration_time': 1.2, 'led_pin': 9,
                        'pull_up_down': 'test_pull_up_down'}
        mock_init = func_test_generateDevice_type(gpio_control_class, name, configArray, ShutdownButton)
        mock_init.assert_called_once_with(pin=5, action="test_funcCall1-test_funcCall1Args",
                                          name=name, bouncetime=299, antibouncehack=True, edge='test_edge',
                                          hold_time=1.3, iteration_time=1.2, led_pin=9,
                                          pull_up_down='test_pull_up_down')

    def test_generateDevice_TwoButtonControl_default(self, gpio_control_class):
        name = 'TEST_TwoButtonControl'
        configArray = {'Type': TwoButtonControl.__name__, 'Pin1': '5', 'Pin2': '6',
                        'functionCall1': 'test_funcCall1',
                        'functionCall2': 'test_funcCall2',
                        'functionCallTwoButtons': 'test_funcCallTwoButtons'}
        mock_init = func_test_generateDevice_type(gpio_control_class, name, configArray, TwoButtonControl)
        mock_init.assert_called_once_with(5, 6, "test_funcCall1-None", "test_funcCall2-None",
                                          functionCallTwoBtns="test_funcCallTwoButtons-None",
                                          pull_up_down='pull_up', hold_mode=None, hold_time=0.3,
                                          bouncetime=500, edge='falling', antibouncehack=False, name=name)

    def test_generateDevice_TwoButtonControl(self, gpio_control_class):
        name = 'TEST_TwoButtonControl'
        configArray = {'Type': TwoButtonControl.__name__, 'Pin1': '5', 'Pin2': '6',
                        'functionCall1': 'test_funcCall1', 'functionCall1Args': 'test_funcCall1Args',
                        'functionCall2': 'test_funcCall2', 'functionCall2Args': 'test_funcCall2Args',
                        'functionCallTwoButtons': 'test_funcCallTwoButtons',
                        'functionCallTwoButtonsArgs': 'test_funcCallTwoButtonsArgs',
                        'pull_up_down': 'test_pull_up_down', 'hold_mode': 'test_holdmode', 'hold_time': 1.3,
                        'bouncetime': 299, 'edge': 'test_edge', 'antibouncehack': 'True'}
        mock_init = func_test_generateDevice_type(gpio_control_class, name, configArray, TwoButtonControl)
        mock_init.assert_called_once_with(5, 6, "test_funcCall1-test_funcCall1Args", "test_funcCall2-test_funcCall2Args",
                                          functionCallTwoBtns="test_funcCallTwoButtons-test_funcCallTwoButtonsArgs",
                                          pull_up_down='test_pull_up_down', hold_mode='test_holdmode', hold_time=1.3,
                                          bouncetime=299, edge='test_edge', antibouncehack=True, name=name)

    # ---------------

    def test_getFunctionCall_None_None(self, gpio_control_class):
        result = gpio_control_class.getFunctionCall(None, None)
        assert result(()) is None
        result = gpio_control_class.getFunctionCall('None', None)
        assert result(()) is None
        result = gpio_control_class.getFunctionCall("nonExisting", None)
        assert result(()) is None

    def test_getFunctionCall_withoutParam(self, gpio_control_class):
        result = gpio_control_class.getFunctionCall("funcTestWithoutParameter", None)
        assert result(()) == "funcTestWithoutParameter"

    def test_getFunctionCall_withParam(self, gpio_control_class):
        result = gpio_control_class.getFunctionCall("funcTestWithParameter", "param1")
        assert result(()) == "funcTestWithParameter(param1)"

    # ---------------

    def test_printAllDevices_empty(self, gpio_control_class):
        with patch('builtins.print') as mock_print:
            gpio_control_class.print_all_devices()
            mock_print.assert_not_called

    def test_printAllDevices_list(self, gpio_control_class):
        with patch('builtins.print') as mock_print:
            gpio_control_class.devices = ["test1", "test2"]
            gpio_control_class.print_all_devices()
            mock_print.assert_has_calls([call("test1"), call("test2")])
