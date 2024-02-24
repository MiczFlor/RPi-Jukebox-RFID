import pytest
from mock import MagicMock
from ..GPIODevices.simple_button import SimpleButton, GPIO


mockedAction = MagicMock()
mockedSecAction = MagicMock()


@pytest.fixture
def simple_button():
    mockedAction.reset_mock()
    mockedSecAction.reset_mock()

    return SimpleButton(pin=1, action=mockedAction, action2=mockedSecAction, name='TestButton')


class TestButton:

    def test_init(self):
        SimpleButton(pin=1)

    def test_init_edge_valid(self):
        SimpleButton(pin=1, edge='falling')
        SimpleButton(pin=1, edge='rising')
        SimpleButton(pin=1, edge='both')
        SimpleButton(pin=1, edge=GPIO.FALLING)
        SimpleButton(pin=1, edge=GPIO.RISING)
        SimpleButton(pin=1, edge=GPIO.BOTH)

    def test_init_edge_invalid(self):
        with pytest.raises(KeyError) as e:
            SimpleButton(pin=1, edge='invalid')
        assert str(e.value) == "'Unknown Edge type invalid'"

    def test_init_pullUpDown_valid(self):
        SimpleButton(pin=1, pull_up_down='pull_up')
        SimpleButton(pin=1, pull_up_down='pull_down')
        SimpleButton(pin=1, pull_up_down='pull_off')
        SimpleButton(pin=1, pull_up_down=GPIO.PUD_UP)
        SimpleButton(pin=1, pull_up_down=GPIO.PUD_DOWN)
        SimpleButton(pin=1, pull_up_down=GPIO.PUD_OFF)

    def test_init_pullUpDown_invalid(self):
        with pytest.raises(KeyError) as e:
            SimpleButton(pin=1, pull_up_down="invalid")
        assert str(e.value) == "'Unknown Pull Up/Down type invalid'"

    def test_is_pressed_pullUp(self):
        simple_button = SimpleButton(pin=1, pull_up_down='pull_up')
        GPIO.input.side_effect = [False]
        is_pressed = simple_button.is_pressed
        assert is_pressed is True
        GPIO.input.side_effect = [True]
        is_pressed = simple_button.is_pressed
        assert is_pressed is False

    # TODO is pull_up always true a bug?
    # def test_is_pressed_pullDown(self):
    #     simple_button = SimpleButton(pin=1, pull_up_down='pull_up')
    #     GPIO.input.side_effect = [False]
    #     is_pressed = simple_button.is_pressed
    #     assert is_pressed is False
    #     GPIO.input.side_effect = [True]
    #     is_pressed = simple_button.is_pressed
    #     assert is_pressed is True

    def test_antibounce(self, simple_button):
        simple_button.antibouncehack = True
        GPIO.input.side_effect = lambda *args: 1
        simple_button.callbackFunctionHandler()
        mockedAction.assert_not_called()
        mockedSecAction.assert_not_called()

    def test_callback(self, simple_button):
        simple_button.callbackFunctionHandler(simple_button.pin)
        mockedAction.assert_called_once_with()
        mockedSecAction.assert_not_called()

    def test_callback_without_pin_argument(self, simple_button):
        simple_button.callbackFunctionHandler()
        mockedAction.assert_called_once_with()
        mockedSecAction.assert_not_called()

    def test_callback_with_wrong_pin_argument(self, simple_button):
        simple_button.callbackFunctionHandler(simple_button.pin + 1)
        mockedAction.assert_called_once_with(simple_button.pin + 1)
        mockedSecAction.assert_not_called()

    def test_callback_with_more_arguments(self, simple_button):
        simple_button.callbackFunctionHandler(simple_button.pin, 5)
        mockedAction.assert_called_once_with(5)
        mockedSecAction.assert_not_called()

    def test_change_new_action(self, simple_button):
        simple_button.callbackFunctionHandler(simple_button.pin, 5)

        newMockedAction = MagicMock()
        simple_button.when_pressed = newMockedAction
        simple_button.callbackFunctionHandler(simple_button.pin)

        newMockedAction.assert_called_once_with()
        mockedAction.assert_called_once_with(5)
        mockedSecAction.assert_not_called()

    def test_hold_Repeat_longer_holdtime(self, simple_button):
        GPIO.LOW = 0
        GPIO.input.side_effect = [False, False, False, True]
        simple_button.hold_time = 0
        simple_button.hold_mode = 'Repeat'
        calls = mockedAction.call_count
        simple_button.callbackFunctionHandler(simple_button.pin)
        assert mockedAction.call_count - calls == 4
        mockedSecAction.assert_not_called()

    def test_hold_Repeat_shorter_holdtime(self, simple_button):
        GPIO.LOW = 0
        GPIO.input.side_effect = [False, True]
        simple_button.hold_time = 0.3
        simple_button.hold_mode = 'Repeat'
        calls = mockedAction.call_count
        simple_button.callbackFunctionHandler(simple_button.pin)
        assert mockedAction.call_count - calls == 1
        mockedSecAction.assert_not_called()

    def test_hold_Postpone_longer_holdtime(self, simple_button):
        GPIO.LOW = 0
        GPIO.input.side_effect = [False, False, False, True]
        simple_button.hold_time = 0
        simple_button.hold_mode = 'Postpone'
        calls = mockedAction.call_count
        simple_button.callbackFunctionHandler(simple_button.pin)
        assert mockedAction.call_count - calls == 1
        mockedSecAction.assert_not_called()

    def test_hold_Postpone_shorter_holdtime(self, simple_button):
        GPIO.LOW = 0
        GPIO.input.side_effect = [False, True, True]
        simple_button.hold_time = 0.3
        simple_button.hold_mode = 'Postpone'
        calls = mockedAction.call_count
        simple_button.callbackFunctionHandler(simple_button.pin)
        assert mockedAction.call_count - calls == 0
        mockedSecAction.assert_not_called()

    def test_hold_SecondFunc_longer_holdtime(self, simple_button):
        GPIO.LOW = 0
        GPIO.input.side_effect = [False, False, False, True]
        simple_button.hold_time = 0
        simple_button.hold_mode = 'SecondFunc'
        calls = mockedSecAction.call_count
        simple_button.callbackFunctionHandler(simple_button.pin)
        mockedAction.assert_called_once()
        assert mockedSecAction.call_count - calls == 1

    def test_hold_SecondFunc_shorter_holdtime(self, simple_button):
        GPIO.LOW = 0
        GPIO.input.side_effect = [False, True, True]
        simple_button.hold_time = 0.3
        simple_button.hold_mode = 'SecondFunc'
        calls = mockedSecAction.call_count
        simple_button.callbackFunctionHandler(simple_button.pin)
        mockedAction.assert_called_once()
        assert mockedSecAction.call_count - calls == 0

    def test_hold_SecondFuncRepeat_longer_holdtime(self, simple_button):
        GPIO.LOW = 0
        GPIO.input.side_effect = [False, False, False, True]
        simple_button.hold_time = 0
        simple_button.hold_mode = 'SecondFuncRepeat'
        calls = mockedSecAction.call_count
        simple_button.callbackFunctionHandler(simple_button.pin)
        mockedAction.assert_called_once()
        assert mockedSecAction.call_count - calls == 3

    def test_hold_SecondFuncRepeat_shorter_holdtime(self, simple_button):
        GPIO.LOW = 0
        GPIO.input.side_effect = [False, True, True]
        simple_button.hold_time = 0.3
        simple_button.hold_mode = 'SecondFuncRepeat'
        calls = mockedSecAction.call_count
        simple_button.callbackFunctionHandler(simple_button.pin)
        mockedAction.assert_called_once()
        assert mockedSecAction.call_count - calls == 0

    def test_repr(self):
        button = SimpleButton(name='test_repr', pin=1, edge='rising', hold_mode=None, hold_time=2.5,
                              bouncetime=500, antibouncehack=True, pull_up_down='pull_down')
        expected = ('<SimpleButton-test_repr(pin=1,edge=rising,hold_mode=None,hold_time=2.5,bouncetime=500,'
                    'antibouncehack=True,pull_up_down=pull_down)>')
        assert repr(button) == expected
