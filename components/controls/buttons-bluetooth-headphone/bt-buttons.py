#!/usr/bin/env python3
"""
Enable Bluetooth Headphone/Speaker Buttons for Music Control

Script will listen to headphone button press events and call appropriate Phoniebox control function
If no headset is connected, it will endlessly check headset connection status every 2 seconds.

Should be run as service. For debug can be run directly from console with additional debug output:
  $ ./bt-buttons.py debug

- Run install-bt-buttons.sh to configure user rights, service etc (will also run bt-buttons-register-device.py)
- Run bt-buttons-register-device.py with headphones connected to select bluetooth input device

This script has been tested with the following headsets: PowerLocus Buddy, Sennheiser Momentum M2 AEBT
"""
import evdev as ev
import logging
import subprocess
import time
import sys
import os.path


# Filename with stored device name, relative to this script's location
filename_device_selection = '../../../settings/bluetooth-input-device-name.txt'
# Filename to read bt-sink-switch / mpd support from
# See components/bluetooth-audio-toggle for more information
filename_mpd_switch_feature = '../../../settings/bluetooth-sink-switch'


# Button key codes
bt_keycode_play = 200
bt_keycode_pause = 201
bt_keycode_next = 163
bt_keycode_prev = 165


# Create logger
logger = logging.getLogger('bt-buttons.py')
logger.setLevel(logging.DEBUG)
# Create console handler and set level to debug
logconsole = logging.StreamHandler()
logconsole.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s: %(message)s', datefmt='%d.%m.%Y %H:%M:%S'))
logconsole.setLevel(logging.DEBUG)
logger.addHandler(logconsole)


def bt_on_disconnect(mpd_support=0) -> None:
    """Executed on Bluetooth device disconnect

    Default: Switch output device to speakers
    Disconnecting the Bluetooth device during playback causes an error with mpd
    as it suddenly has no more output stream. Error state is checked and previous state recovery is attempted to
    provide smooth transistion to speakers automatically by bt-sink-switch.py
    :param mpd_support: Indicates if bluetooth sink switch feature using mpd is enabled
    """
    logger.info("on disconnect")
    if mpd_support:
        pctproc = subprocess.run(f"{os.path.dirname(os.path.realpath(__file__))}/../../../scripts/playout_controls.sh -c=bluetoothtoggle -v=speakers", shell=True, check=False,
                                 stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        logger.debug(pctproc.stdout)


def bt_on_connect(mpd_support=0) -> None:
    """Executed on Bluetooth device connect

    Default: Switch output device to Bluetooth device
    Note: During bootup, if bluetooth device gets connected before the service for this script is started, this function
    will still be executed
    :param mpd_support: Indicates if bluetooth sink switch feature using mpd is enabled
    """
    logger.info("on connect")
    if mpd_support:
        pctproc = subprocess.run(f"{os.path.dirname(os.path.realpath(__file__))}/../../../scripts/playout_controls.sh -c=bluetoothtoggle -v=headphones", shell=True, check=False,
                                 stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        logger.debug(pctproc.stdout)


def bt_get_device_name(filename) -> str:
    """Gets the bluetooth device name from config file"""
    logger.debug(f"bt_get_device_name looking for '{filename}'")
    try:
        with open(filename) as f:
            devname: str = f.readline().strip()
    except Exception as e:
        logger.critical("#" * 60)
        logger.critical(f"Error opening file '{filename}'. Please run registerBluetoothInput.py first!")
        logger.critical(f"Exception: {e.__class__.__name__}")
        logger.critical("#" * 60)
        raise e
    logger.debug(f"bt_get_device_name() -> {devname}")
    return devname


def bt_get_mpd_support(filename) -> int:
    """Checks if bluetooth switch feature is enabled"""
    logger.debug(f"bt_get_mpd_support looking for '{filename}'")
    try:
        with open(filename) as f:
            mpdsupport = f.readline().strip().lower()
    except PermissionError:
        mpdsupport = ''
    except FileNotFoundError:
        mpdsupport = ''
    logger.debug(f"file read out '{mpdsupport}'")
    if mpdsupport == 'enabled':
        logger.debug("bt_get_mpd_support result is ON")
        return 1
    logger.debug("bt_get_mpd_support result is OFF")
    return 0


def bt_open_device(name) -> ev.InputDevice:
    """Tries to open bluetooth device, raises error if not available to be handled up-level"""
    all_devices = [ev.InputDevice(path) for path in ev.list_devices()]
    for dev in all_devices:
        if dev.name == name:
            logger.debug(f"bt_open_device({name}): Device '{name}' search success")
            break
    else:
        # No device found, don't log to prevent log file spamming
        # logger.error(f"bt_open_device({name}): Device '{name}' not found")
        raise FileNotFoundError
    return dev


def bt_key_handler(name, mpd_support=0) -> None:
    """Actual key handler, once bluetooth device is connected"""
    # Try to open the event device, will exit with exception on fail
    dev = bt_open_device(name)
    logger.debug(dev)
    bt_on_connect(mpd_support)
    path = os.path.dirname(os.path.realpath(__file__))
    # Infinite loop reading the events. Will fail, if event device gets disconnected
    for event in dev.read_loop():
        if event.type == ev.ecodes.EV_KEY:
            # Report the button event
            logger.debug(ev.categorize(event))
            # Only act on button press, not button release
            if event.value == 1:
                if event.code == bt_keycode_play:
                    proc = subprocess.run(f"{path}/../../../scripts/playout_controls.sh -c=playerpause", shell=True, check=False,
                                          stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
                elif event.code == bt_keycode_pause:
                    proc = subprocess.run(f"{path}/../../../scripts/playout_controls.sh -c=playerpause", shell=True, check=False,
                                          stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
                elif event.code == bt_keycode_next:
                    proc = subprocess.run(f"{path}/../../../scripts/playout_controls.sh -c=playernext", shell=True, check=False,
                                          stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
                elif event.code == bt_keycode_prev:
                    proc = subprocess.run(f"{path}/../../../scripts/playout_controls.sh -c=playerprev", shell=True, check=False,
                                          stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
                logger.debug(proc.stdout)
                if proc.returncode != 0:
                    logger.error("#" * 60)
                    logger.error(f"In subprocess execution (retcode = {str(proc.returncode())})")
                    logger.error(proc.stdout)
                    logger.error("#" * 60)


def bt_loop(filename_device_selection, filename_mpd_switch_feature, sleeptime=2) -> None:
    """Main loop for watching bluetooth device to connect, then call bt_key_handler

    Constantly checks for bluetooth device to connect by calling bt_key_handler()
    On bluetooth device connect bt_on_connect will be executed
    On bluetooth device disconnect bt_on_disconnect will be executed

    :param filename_mpd_switch_feature: Filename with stored device name, relative to this script's location
    :param filename_device_selection: Filename with bluetooth sink switch configuration, relative to this script's location
    :param sleeptime: Time to sleep between bluetooth device connection checks
    :return:
    """
    path = os.path.dirname(os.path.realpath(__file__))
    filename = path + '/' + filename_device_selection
    name = bt_get_device_name(filename)
    filename = path + '/' + filename_mpd_switch_feature
    mpd_support = bt_get_mpd_support(filename)
    logger.debug('Waiting for first connect of Bluetooth device')
    while True:
        try:
            bt_key_handler(name, mpd_support)
        except FileNotFoundError:
            # This error occurs, if opening the bluetooth input device fails
            time.sleep(sleeptime)
        except OSError:
            # This error occurs, when the already opened bluetooth device suddenly gets disconnected
            bt_on_disconnect(mpd_support)
            time.sleep(sleeptime)


if __name__ == '__main__':
    if len(sys.argv) == 2:
        logconsole.setLevel(logging.DEBUG)
    bt_loop(filename_device_selection, filename_mpd_switch_feature, sleeptime=2)
