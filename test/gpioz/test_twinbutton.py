# Copyright (c) 2022 Chris Banz
#
# SPDX-License-Identifier: MIT License
#
import sys
import os
import time

from gpiozero import Device
from gpiozero.pins.mock import MockFactory, MockPin

# In case this is run locally from
sys.path.append(os.path.abspath('../../src/jukebox'))
from components.gpio.gpioz.core.input_devices import TwinButton  # noqa: E402

Device.pin_factory = MockFactory(pin_class=MockPin)


class Incrementer:
    def __init__(self):
        self._value_a = 0
        self._value_b = 0
        self._value_ab = 0
        self._held_a = 0
        self._held_b = 0
        self._held_ab = 0

    def increment_a(self):
        print("incr A")
        self._value_a += 1

    def increment_b(self):
        print("incr B")
        self._value_b += 1

    def increment_ab(self):
        print("incr AB")
        self._value_ab += 1

    def increment_held_a(self):
        print("incr HELD A")
        self._held_a += 1

    def increment_held_b(self):
        print("incr HELD B")
        self._held_b += 1

    def increment_held_ab(self):
        print("incr HELD AB")
        self._held_ab += 1

    @property
    def value_a(self):
        return self._value_a

    @property
    def value_b(self):
        return self._value_b

    @property
    def value_ab(self):
        return self._value_ab

    @property
    def held_a(self):
        return self._held_a

    @property
    def held_b(self):
        return self._held_b

    @property
    def held_ab(self):
        return self._held_ab


def init(btn: TwinButton, inc: Incrementer):
    btn.on_short_press_a = inc.increment_a
    btn.on_short_press_b = inc.increment_b
    btn.on_short_press_ab = inc.increment_ab
    btn.on_long_press_a = inc.increment_held_a
    btn.on_long_press_b = inc.increment_held_b
    btn.on_long_press_ab = inc.increment_held_ab


def press(btn):
    btn.pin.drive_low()


def release(btn):
    btn.pin.drive_high()


def assert_cnt(inc, a, b, ab, held_a, held_b, held_ab):
    assert inc.value_a == a
    assert inc.value_b == b
    assert inc.value_ab == ab
    assert inc.held_a == held_a
    assert inc.held_b == held_b
    assert inc.held_ab == held_ab


def test_press_short_a():
    inc = Incrementer()
    with TwinButton(20, 21) as btn:
        init(btn, inc)
        press(btn._pin_a)
        release(btn._pin_a)
    assert_cnt(inc, 1, 0, 0, 0, 0, 0)
    assert btn._state == TwinButton.StateVar.IDLE


def test_press_short_a_wo_hold():
    inc = Incrementer()
    with TwinButton(20, 21, hold_time=0.2, hold_repeat=True) as btn:
        init(btn, inc)
        btn.on_long_press_a = None
        press(btn._pin_a)
        time.sleep(2 * btn.hold_time + 0.1)
        release(btn._pin_a)
    assert_cnt(inc, 1, 0, 0, 0, 0, 0)
    assert btn._state == TwinButton.StateVar.IDLE


# -------------------------------------------------------------------------------------------

def test_press_long_a():
    inc = Incrementer()
    with TwinButton(20, 21, hold_time=0.2, hold_repeat=True) as btn:
        init(btn, inc)
        press(btn._pin_a)
        time.sleep(btn.hold_time + 0.1)
        release(btn._pin_a)
    assert_cnt(inc, 0, 0, 0, 1, 0, 0)
    assert btn._state == TwinButton.StateVar.IDLE


def test_press_long_a_w_repeat():
    inc = Incrementer()
    with TwinButton(20, 21, hold_time=0.2, hold_repeat=True) as btn:
        init(btn, inc)
        press(btn._pin_a)
        time.sleep(3 * btn.hold_time + 0.1)
        release(btn._pin_a)
    assert_cnt(inc, 0, 0, 0, 3, 0, 0)
    assert btn._state == TwinButton.StateVar.IDLE


def test_press_long_a_wo_repeat():
    inc = Incrementer()
    with TwinButton(20, 21, hold_time=0.2, hold_repeat=False) as btn:
        init(btn, inc)
        press(btn._pin_a)
        time.sleep(3 * btn.hold_time + 0.1)
        release(btn._pin_a)
    assert_cnt(inc, 0, 0, 0, 1, 0, 0)
    assert btn._state == TwinButton.StateVar.IDLE


# -------------------------------------------------------------------------------------------

def test_press_long_a_interfere_b_v1_1():
    inc = Incrementer()
    with TwinButton(20, 21, hold_time=0.2, hold_repeat=True) as btn:
        init(btn, inc)
        press(btn._pin_a)
        time.sleep(btn.hold_time + 0.1)
        press(btn._pin_b)
        release(btn._pin_b)
        release(btn._pin_a)
    assert_cnt(inc, 0, 0, 0, 1, 0, 0)
    assert btn._state == TwinButton.StateVar.IDLE


def test_press_long_a_interfere_b_v1_2():
    inc = Incrementer()
    with TwinButton(20, 21, hold_time=0.2, hold_repeat=True) as btn:
        init(btn, inc)
        btn.on_long_press_a = None
        press(btn._pin_a)
        time.sleep(btn.hold_time + 0.1)
        press(btn._pin_b)
        release(btn._pin_b)
        release(btn._pin_a)
    assert_cnt(inc, 1, 0, 0, 0, 0, 0)
    assert btn._state == TwinButton.StateVar.IDLE


def test_press_long_a_interfere_b_v2_1():
    inc = Incrementer()
    with TwinButton(20, 21, hold_time=0.2, hold_repeat=True) as btn:
        init(btn, inc)
        press(btn._pin_a)
        time.sleep(btn.hold_time + 0.1)
        press(btn._pin_b)
        release(btn._pin_a)
        release(btn._pin_b)
    assert_cnt(inc, 0, 0, 0, 1, 0, 0)
    assert btn._state == TwinButton.StateVar.IDLE


def test_press_long_a_interfere_b_v2_2():
    inc = Incrementer()
    with TwinButton(20, 21, hold_time=0.2, hold_repeat=True) as btn:
        init(btn, inc)
        btn.on_long_press_a = None
        press(btn._pin_a)
        time.sleep(btn.hold_time + 0.1)
        press(btn._pin_b)
        release(btn._pin_a)
        release(btn._pin_b)
    assert_cnt(inc, 1, 0, 0, 0, 0, 0)
    assert btn._state == TwinButton.StateVar.IDLE


# -------------------------------------------------------------------------------------------

def test_press_long_a_toggle_a():
    inc = Incrementer()
    with TwinButton(20, 21, hold_time=0.2, hold_repeat=True) as btn:
        init(btn, inc)
        press(btn._pin_a)
        time.sleep(btn.hold_time + 0.1)
        press(btn._pin_b)
        release(btn._pin_a)
        time.sleep(btn.hold_time + 0.1)
        press(btn._pin_a)
        time.sleep(btn.hold_time + 0.1)
        release(btn._pin_b)
        release(btn._pin_a)
    assert_cnt(inc, 0, 0, 0, 1, 0, 0)
    assert btn._state == TwinButton.StateVar.IDLE


# -------------------------------------------------------------------------------------------

def test_press_short_ab():
    inc = Incrementer()
    with TwinButton(20, 21) as btn:
        init(btn, inc)
        press(btn._pin_a)
        press(btn._pin_b)
        release(btn._pin_a)
        release(btn._pin_b)
    assert_cnt(inc, 0, 0, 1, 0, 0, 0)
    assert btn._state == TwinButton.StateVar.IDLE


def test_press_short_ab_wo_hold():
    inc = Incrementer()
    with TwinButton(20, 21) as btn:
        init(btn, inc)
        btn.on_long_press_ab = None
        press(btn._pin_a)
        press(btn._pin_b)
        time.sleep(btn.hold_time + 0.1)
        assert_cnt(inc, 0, 0, 1, 0, 0, 0)
        release(btn._pin_a)
        release(btn._pin_b)
    assert_cnt(inc, 0, 0, 1, 0, 0, 0)
    assert btn._state == TwinButton.StateVar.IDLE


def test_press_short_ab_by_asymmetric_activation():
    inc = Incrementer()
    with TwinButton(20, 21, hold_time=0.2) as btn:
        init(btn, inc)
        press(btn._pin_a)
        time.sleep(0.1)
        press(btn._pin_b)
        # Make sure A hold time is triggered, but
        # before B hold time is not reached before the button is released --> trigger press_short
        time.sleep(0.11)
        release(btn._pin_a)
        release(btn._pin_b)
    assert_cnt(inc, 0, 0, 1, 0, 0, 0)
    assert btn._state == TwinButton.StateVar.IDLE


def test_press_short_ab_toggle_a():
    inc = Incrementer()
    with TwinButton(20, 21, hold_time=0.2) as btn:
        init(btn, inc)
        press(btn._pin_a)
        press(btn._pin_b)
        release(btn._pin_a)
        assert_cnt(inc, 0, 0, 1, 0, 0, 0)
        press(btn._pin_a)
        release(btn._pin_a)
        press(btn._pin_a)
        release(btn._pin_b)
        release(btn._pin_a)
    assert_cnt(inc, 0, 0, 1, 0, 0, 0)
    assert btn._state == TwinButton.StateVar.IDLE


def test_press_short_ab_toggle_b():
    inc = Incrementer()
    with TwinButton(20, 21) as btn:
        init(btn, inc)
        press(btn._pin_a)
        press(btn._pin_b)
        release(btn._pin_b)
        assert_cnt(inc, 0, 0, 1, 0, 0, 0)
        press(btn._pin_b)
        release(btn._pin_b)
        press(btn._pin_b)
        release(btn._pin_a)
        press(btn._pin_a)
        release(btn._pin_b)
        release(btn._pin_a)
    assert_cnt(inc, 0, 0, 1, 0, 0, 0)
    assert btn._state == TwinButton.StateVar.IDLE


def test_press_short_ab_toggle_a_wo_hold():
    inc = Incrementer()
    with TwinButton(20, 21, hold_time=0.2) as btn:
        init(btn, inc)
        btn.on_long_press_ab = None
        press(btn._pin_a)
        press(btn._pin_b)
        assert_cnt(inc, 0, 0, 1, 0, 0, 0)
        release(btn._pin_a)
        press(btn._pin_a)
        release(btn._pin_a)
        press(btn._pin_a)
        release(btn._pin_b)
        release(btn._pin_a)
    assert_cnt(inc, 0, 0, 1, 0, 0, 0)
    assert btn._state == TwinButton.StateVar.IDLE


def test_press_short_ab_toggle_b_wo_hold():
    inc = Incrementer()
    with TwinButton(20, 21) as btn:
        init(btn, inc)
        btn.on_long_press_ab = None
        press(btn._pin_a)
        press(btn._pin_b)
        assert_cnt(inc, 0, 0, 1, 0, 0, 0)
        release(btn._pin_b)
        press(btn._pin_b)
        release(btn._pin_b)
        press(btn._pin_b)
        release(btn._pin_a)
        press(btn._pin_a)
        release(btn._pin_b)
        release(btn._pin_a)
    assert_cnt(inc, 0, 0, 1, 0, 0, 0)
    assert btn._state == TwinButton.StateVar.IDLE


# -------------------------------------------------------------------------------------------

def test_press_long_ab():
    inc = Incrementer()
    with TwinButton(20, 21, hold_time=0.2) as btn:
        init(btn, inc)
        press(btn._pin_a)
        press(btn._pin_b)
        time.sleep(btn.hold_time + 0.1)
        release(btn._pin_a)
        release(btn._pin_b)
    assert_cnt(inc, 0, 0, 0, 0, 0, 1)
    assert btn._state == TwinButton.StateVar.IDLE


def test_press_long_ab_wo_held():
    inc = Incrementer()
    with TwinButton(20, 21, hold_time=0.2) as btn:
        init(btn, inc)
        btn.on_long_press_ab = None
        press(btn._pin_a)
        press(btn._pin_b)
        time.sleep(btn.hold_time + 0.1)
        release(btn._pin_a)
        release(btn._pin_b)
    assert_cnt(inc, 0, 0, 1, 0, 0, 0)
    assert btn._state == TwinButton.StateVar.IDLE


def test_press_long_ab_w_repeat():
    inc = Incrementer()
    with TwinButton(20, 21, hold_time=0.2, hold_repeat=True) as btn:
        init(btn, inc)
        press(btn._pin_a)
        press(btn._pin_b)
        time.sleep(3 * btn.hold_time + 0.1)
        release(btn._pin_a)
        release(btn._pin_b)
    assert_cnt(inc, 0, 0, 0, 0, 0, 1)
    assert btn._state == TwinButton.StateVar.IDLE


if __name__ == '__main__':
    print("*" * 20)
    test_press_short_a()
    print("*" * 20)
    test_press_short_a_wo_hold()
    print("*" * 20)
    test_press_long_a()
    print("*" * 20)
    test_press_long_a_w_repeat()
    print("*" * 20)
    test_press_long_a_wo_repeat()

    print("*" * 20)
    test_press_long_a_interfere_b_v1_1()
    print("*" * 20)
    test_press_long_a_interfere_b_v1_2()
    print("*" * 20)
    test_press_long_a_interfere_b_v2_1()
    print("*" * 20)
    test_press_long_a_interfere_b_v2_2()

    print("*" * 20)
    test_press_long_a_toggle_a()

    print("*" * 20)
    test_press_short_ab()
    print("*" * 20)
    test_press_short_ab_wo_hold()
    print("*" * 20)
    test_press_short_ab_by_asymmetric_activation()

    print("*" * 20)
    test_press_short_ab_toggle_a()
    print("*" * 20)
    test_press_short_ab_toggle_b()

    test_press_short_ab_toggle_a_wo_hold()
    test_press_short_ab_toggle_b_wo_hold()

    test_press_long_ab()
    test_press_long_ab_wo_held()
    test_press_long_ab_w_repeat()
