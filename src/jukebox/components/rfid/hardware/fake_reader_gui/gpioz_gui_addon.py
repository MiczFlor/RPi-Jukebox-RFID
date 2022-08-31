# RPi-Jukebox-RFID Version 3
# Copyright (c) See file LICENSE in project root folder
"""
Add GPIO input devices and output devices to the RFID Mock Reader GUI
"""
import gpiozero
import logging
import functools
import time
import tkinter as tk
from tkinter import ttk
import components.gpio.gpioz as gpioz
from components.gpio.gpioz.core.input_devices import Button, ShortLongPressButton, LongPressButton, RotaryEncoder
from components.rfid.hardware.fake_reader_gui.fake_reader_gui import action_que

logger = logging.getLogger('jb.rfid.tk')


def _gpioz_press_short(device):
    """
    Simulate a short press on an input device
    """
    logger.debug(f"Press button short {device.pin.number}")
    # Drive low is low level function --> need to adjust level according to _active_state
    delay = 0.01 if device.pin.bounce is None else 0.01 + device.pin.bounce
    if device._button._active_state is False:
        device.pin.drive_low()
    else:
        device.pin.drive_high()
    time.sleep(delay)
    if device._button._active_state is False:
        device.pin.drive_high()
    else:
        device.pin.drive_low()


def _gpioz_press_long(device):
    """
    Simulate a long press on an input device. Long means longer than the configured hold_time
    """
    logger.debug(f"Press button long {device.pin.number}")
    delay = device.hold_time + 0.05
    if device.pin.bounce is not None:
        delay += device.pin.bounce

    if device._button._active_state is False:
        device.pin.drive_low()
    else:
        device.pin.drive_high()
    time.sleep(delay)
    if device._button._active_state is False:
        device.pin.drive_high()
    else:
        device.pin.drive_low()


def _gpioz_rotate_cw(device):
    """Simulate a clockwise rotation"""
    # Pattern taken directly from the GPIOZero test suite:
    # https://github.com/gpiozero/gpiozero/blob/2b6aa5314830fedf3701113b6713161086defa38/tests/test_inputs.py#L332
    device.pin_a.drive_low()
    device.pin_b.drive_low()
    device.pin_a.drive_high()
    device.pin_b.drive_high()


def _gpioz_rotate_ccw(device):
    """Simulate a counter-clockwise rotation"""
    device.pin_b.drive_low()
    device.pin_a.drive_low()
    device.pin_b.drive_high()
    device.pin_a.drive_high()


def create_inputs(frame, default_btn_width, default_padx, default_pady):
    """
    Add all input devies to the GUI

    :param frame: The TK frame (e.g. LabelFrame) in the main GUI to add the buttons to
    :return: List of all added GUI buttons
    """

    _gpoioz_input_devices = []
    idx = 0
    for name, device in gpioz.plugin.input_devices.items():
        if isinstance(device, Button):
            lbl = ttk.Label(frame, text=f"{name}\n(Button, Pin={device.pin.number}, PullUp={device.pull_up})", padding=0)
            lbl.grid(column=0, row=idx, padx=default_padx, pady=default_pady, sticky='NSEW', columnspan=2)
            idx += 1
            btn = ttk.Button(frame, text='Press  ⇅', width=default_btn_width,
                             command=functools.partial(_gpioz_press_short, device=device))
            btn.grid(column=0, row=idx, padx=default_padx, pady=0, sticky='NSEW')
            idx += 1
            _gpoioz_input_devices.append(btn)
        elif isinstance(device, LongPressButton):
            lbl = ttk.Label(frame, text=f"{name}\n(LongPressButton, Pin={device.pin.number}, PullUp={device.pull_up})",
                            padding=0)
            lbl.grid(column=0, row=idx, padx=default_padx, pady=default_pady, sticky='NSEW', columnspan=2)
            idx += 1
            btn = ttk.Button(frame, text='Long Press  ↳', width=default_btn_width,
                             command=functools.partial(_gpioz_press_long, device=device))
            btn.grid(column=0, row=idx, padx=default_padx, pady=0, sticky='NSEW')
            idx += 1
            _gpoioz_input_devices.append(btn)
        elif isinstance(device, ShortLongPressButton):
            lbl = ttk.Label(frame, text=f"{name}\n(ShortLongPressButton, Pin={device.pin.number}, PullUp={device.pull_up})",
                            padding=0)
            lbl.grid(column=0, row=idx, padx=default_padx, pady=default_pady, sticky='NSEW', columnspan=2)
            idx += 1
            btn0 = ttk.Button(frame, text='Press Short ⇅', width=default_btn_width,
                              command=functools.partial(_gpioz_press_short, device=device))
            btn1 = ttk.Button(frame, text='Press Long ↳', width=default_btn_width,
                              command=functools.partial(_gpioz_press_long, device=device))
            btn0.grid(column=0, row=idx, padx=default_padx, pady=0, sticky='NSEW')
            btn1.grid(column=1, row=idx, padx=default_padx, pady=0, sticky='NSEW')
            idx += 1
            _gpoioz_input_devices.append(btn0)
            _gpoioz_input_devices.append(btn1)
        elif isinstance(device, RotaryEncoder):
            lbl = ttk.Label(frame, text=f"{name}\n(RotaryEncoder, PinA={device.pin_a.number}, PinB={device.pin_b.number})",
                            padding=0)
            lbl.grid(column=0, row=idx, padx=default_padx, pady=default_pady, sticky='NSEW', columnspan=2)
            idx += 1
            btn0 = ttk.Button(frame, text='Rotate CW ↻', width=default_btn_width,
                              command=functools.partial(_gpioz_rotate_cw, device=device))
            btn1 = ttk.Button(frame, text='Rotate CCW ↺', width=default_btn_width,
                              command=functools.partial(_gpioz_rotate_ccw, device=device))
            btn0.grid(column=0, row=idx, padx=default_padx, pady=0, sticky='NSEW')
            btn1.grid(column=1, row=idx, padx=default_padx, pady=0, sticky='NSEW')
            idx += 1
            _gpoioz_input_devices.append(btn0)
            _gpoioz_input_devices.append(btn1)

    return _gpoioz_input_devices


def set_state(value, box_state_var):
    """Change the value of a checkbox state variable"""
    box_state_var.set(value)


def que_set_state(value, box_state_var):
    """Queue the action to change a checkbox state variable to the TK GUI main thread"""
    action_que.put(item=(set_state, [value, box_state_var]))


def fix_state(box_state_var):
    """Prevent a checkbox state variable to change on checkbox mouse press"""
    box_state_var.set(1 - box_state_var.get())


def pbox_set_state(value, pbox_state_var, label_var):
    """Update progress bar state and related state label"""
    vint = int(value * 100)
    pbox_state_var.set(vint)
    label_var.configure(text=f"{vint:3}")


def que_set_pbox(value, pbox_state_var, label_var):
    """Queue the action to change the progress bar state to the TK GUI main thread"""
    action_que.put(item=(pbox_set_state, [value, pbox_state_var, label_var]))


def create_outputs(frame, default_btn_width, default_padx, default_pady):
    """
    Add all output devices to the GUI

    :param frame: The TK frame (e.g. LabelFrame) in the main GUI to add the representations to
    :return: List of all added GUI objects
    """
    _gpoioz_output_devices = []
    unsupported = []
    idx = 0
    for name, device in gpioz.plugin.output_devices.items():
        if isinstance(device, gpiozero.LED) or isinstance(device, gpiozero.Buzzer):
            state_var = tk.IntVar()
            # Checkboxes cannot be checked and disabled using the tk-style box['state'] = tk.DISABLED command!
            # As a quick hack, we apply a function that on press reverts the effect of press: fix_state
            cbox = ttk.Checkbutton(frame, text=f"{name} ({device.__class__.__name__}, Pin={device.pin.number})",
                                   variable=state_var,
                                   command=functools.partial(fix_state, state_var))
            cbox.grid(column=0, row=idx, padx=default_padx, pady=default_pady / 2, sticky='NSW')
            # Synchronize the initial state
            state_var.set(device.value)
            idx += 1
            device.on_change_callback = functools.partial(que_set_state, box_state_var=state_var)
            _gpoioz_output_devices.append(cbox)
            _gpoioz_output_devices.append(state_var)
        elif isinstance(device, gpiozero.PWMLED):
            state_var = tk.IntVar()
            lbl = ttk.LabelFrame(frame, text=f"{name} ({device.__class__.__name__}, Pin={device.pin.number})", padding=0)
            lbl.grid(column=0, row=idx, padx=default_padx, pady=default_pady, sticky='NSEW')
            pbox = ttk.Progressbar(lbl, orient=tk.HORIZONTAL, mode='determinate',
                                   length=17 * default_btn_width,
                                   variable=state_var,
                                   style='juke.Horizontal.TProgressbar')
            pbox.grid(column=0, row=0, padx=default_padx, pady=default_pady / 2, sticky='NSW')
            hlbl = ttk.Label(lbl, text='   ', padding=5)
            hlbl.grid(column=1, row=0, padx=0, pady=10)
            _gpoioz_output_devices.append(pbox)
            _gpoioz_output_devices.append(hlbl)
            _gpoioz_output_devices.append(state_var)
            idx += 1
            # Synchronize the initial state
            # because we register the state change event with the output device only now
            # The callback from e.g. volume change to the output device is registered before and the output device has to
            # correct state
            pbox_set_state(device.value, pbox_state_var=state_var, label_var=hlbl)
            device.on_change_callback = functools.partial(que_set_pbox, pbox_state_var=state_var, label_var=hlbl)
        else:
            unsupported.append(f'{name} ({device.__class__.__name__})')
    if len(unsupported) != 0:
        usl = ttk.Label(frame, text="Unsupported devices by GUI:\n - " + "\n - ".join(unsupported), padding=0)
        usl.grid(column=0, row=idx, padx=default_padx, pady=default_pady / 2, sticky='NSW')

    return _gpoioz_output_devices
