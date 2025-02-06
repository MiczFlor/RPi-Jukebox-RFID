#!/usr/bin/env python3
"""
Provides bt_switch (see below) as function and callable script

If called as script, the configuration of led_pin reflecting audio sink status is read from ../../settings/gpio_settings.ini'
See function get_led_pin_configuration for details. If no configuration file is found led_pin is None

Usage:
$ bt-sink-switch cmd [debug]
    cmd = toggle|speakers|headphones : select audio target
    debug                            : enable debug logging
"""
import os
import sys
import re
import subprocess
import logging
import configparser
import time

sys.path.append(os.path.abspath(os.path.dirname(os.path.abspath(__file__)) + "/../gpio_control"))
from GPIODevices import LED  # noqa: E402

# Create logger
logger = logging.getLogger('bt-sink-switch.py')
logger.setLevel(logging.DEBUG)
# Create console handler and set default level
logconsole = logging.StreamHandler()
logconsole.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s: %(message)s', datefmt='%d.%m.%Y %H:%M:%S'))
logconsole.setLevel(logging.INFO)
logger.addHandler(logconsole)


def bt_usage(sname):
    """Print usage, if module is called as script"""
    print("Usage")
    print("  ./" + sname + " toggle | speakers | headphones [debug]")


def bt_check_mpc_err() -> None:
    """Error check on mpd output stream and attempt to recover previous state"""
    logger.debug("bt_check_mpc_err()")
    mpcproc = subprocess.run("mpc status", shell=True, check=False, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    logger.debug(mpcproc.stdout)
    # grep for this expression: 'ERROR: Failed to open audio output'
    mpcerr = re.search(b"ERROR:.*output", mpcproc.stdout)
    if mpcerr is not None:
        mpcplay = subprocess.run("mpc play", shell=True, check=False, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        logger.debug(mpcplay)


def bt_switch(cmd, led_pin=None): # noqa C901
    """
    Set/Toggle between regular speakers and headphone output. If no bluetooth device is connected,
    always defaults to mpc output 1

    To be precise: toggle between mpc output 1 and mpc output 2.

    So, set up your /etc/mpd.conf correctly: first audio_output section should be speakers,
    second audio_output section should be headphones
    To set up bluetooth headphones, follow the wiki
    Short guide to connect bluetooth (without audio setup)
        sudo bluetoothctl
        power on
        agent on
        scan on                   -> shows list of Bluetooth devices in reach
        pair C4:FB:20:63:A7:F2    -> pairing happens
        trust C4:FB:20:63:A7:F2   -> trust you device
        connect C4:FB:20:63:A7:F2 -> connect
        scan off
        exit
    Next time headphones are switched on, they should connect automatically

    Requires
      sudo apt install bluetooth

    Attention
      The user to runs this script (precisly who runs bluetoothctl) needs proper access rights.
      Otherwise bluetoothctl will always return "no default controller found"
      The superuser and users of group "bluetooth" have these. You can check the policy here
        /etc/dbus-1/system.d/bluetooth.conf
      Best to check first if the user which later runs this script can execute bluetoothctl and get meaningful results
        sudo -u www-data bluetoothctl show
      E.g. if you want to do bluetooth manipulation from the web interface, you will most likely need to add www-data
      to the group bluetooth.
      If you want to test this script from the command line, you will most likely need to add user pi
      (or whoever you are) to the group bluetooth or run it as superuser
        sudo usermod -G bluetooth -a www-data
      Don't forget to reboot for group changes to take effect here

    LED support
      If LED number (GPIO number, BCM) is provided, a LED is switched to reflect output sink status
      off = speakers, on = headphones
      LED blinks if no bluetooth device is connected and bluetooth sink is requested, before script default to output 1

      A note for developers: This script is not persistent and only gets called (from various sources)
      when the output sink is changed/toggled and exits.
      This is done to make is callable from button press (gpio button handler), rfid card number, web interface
      The LED state however should be persistent. For that reason no GPIO cleanup is called (ignore warning).

    Parameters
    ----------
    :param cmd: string is "toggle" | "speakers" | "headphones"
    :param led_pin: integer with GPIO pin number of LED to reflect output status. If None, LED support is disabled
    (and no GPIO pin is blocked)
    """
    # Check for valid command
    if cmd != "toggle" and cmd != "speakers" and cmd != "headphones":
        logger.error("Invalid command. Doing nothing.")
        return

    led_device = None
    # Rudimentary check if LED pin request is valid GPIO pin number
    if led_pin is not None:
        if led_pin < 2 or led_pin > 27:
            led_pin = None
            logger.error("Invalid led_pin. Ignoring led_pin = " + str(led_pin))
        else:
            led_device = LED(led_pin, name="BluetoothToggleLed", initial_value=False)

    # Figure out if output 1 (speakers) is enabled
    isSpeakerOn_console = subprocess.run("mpc outputs", shell=True, check=False, stdout=subprocess.PIPE,
                                         stderr=subprocess.STDOUT)
    logger.debug(isSpeakerOn_console.stdout)
    isSpeakerOn = re.search(b"^Output 1.*enabled", isSpeakerOn_console.stdout)

    # Figure out if a bluetooth device is connected (any device will do). Assume here that only speakers/headsets
    # will be connected
    # -> No need for user to adapt MAC address
    # -> will actually support multiple speakers/headsets paired to the phoniebox
    # Alternative: Check for specific bluetooth device only with "bluetoothctl info MACADDRESS"
    isBtConnected_console = subprocess.run("bluetoothctl info", shell=True, check=False, stdout=subprocess.PIPE,
                                           stderr=subprocess.STDOUT)
    logger.debug(isBtConnected_console.stdout)
    isBtConnected = re.search(b"Connected:\s+yes", isBtConnected_console.stdout) # noqa W605

    if (cmd == "toggle" and isSpeakerOn) or (cmd == "headphones"):
        # Only switch to BT headphones if they are actually connected
        if isBtConnected:
            print("Switched audio sink to \"Output 2\"")
            # With mpc enable only 2, output 1 gets disabled before output 2 gets enabled causing a stream output fail
            # This order avoids the issue
            proc = subprocess.run("mpc enable 2; sleep 0.1; mpc disable 1", shell=True, check=False,
                                  stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            logger.debug(proc.stdout)
            # Yet, in some cases, a stream error still occurs: check and recover
            bt_check_mpc_err()
            if led_device is not None:
                led_device.on()
                logger.debug(b'LED on: ' + proc.stdout)
            return
        else:
            print("No bluetooth device connected. Defaulting to \"Output 1\".")
            if led_device is not None:
                sleeptime = 0.25
                for i in range(0, 3):
                    led_device.on()
                    time.sleep(sleeptime)
                    led_device.off()
                    time.sleep(sleeptime)

    # Default: Switch to Speakers
    print("Switched audio sink to \"Output 1\"")
    # mpc only 1 always enables 1 first, avoiding any intermediate state with no valid output stream
    proc = subprocess.run("mpc enable only 1", shell=True, check=False, stdout=subprocess.PIPE,
                          stderr=subprocess.STDOUT)
    logger.debug(proc.stdout)
    # Yet, in some cases, a stream error still occurs: check and recover
    bt_check_mpc_err()
    if led_device is not None:
        led_device.off()
        logger.debug(b'LED off: ' + proc.stdout)


def get_led_pin_config(cfg_file):
    """Read the led pin for reflecting current sink status from cfg_file which is a Python configparser file

    cfg_file is relative to this script's location or an absolute path

    The file must contain the entry

    [BluetoothToggleLed]
    enabled = True
    led_pin = 6

    where
    - led_pin is the BCM number of the GPIO pin (i.e. 'led_pin = 6' means GPIO6) and defaults to None
    - enabled can be used to temporarily disable the LED

    Note: Capitalization of [BluetoothToggleLed] is important!"""

    # Make sure to locate cfg_file relative to this script's location independent of working directory
    if not os.path.isabs(cfg_file):
        cfg_file = os.path.dirname(os.path.realpath(__file__)) + '/' + cfg_file
    logger.debug(f"Reading config file: '{cfg_file}'")
    cfg = configparser.ConfigParser()
    cfg_file_success = cfg.read(cfg_file)
    if not cfg_file_success:
        logger.debug(f"Could not read '{cfg_file}'. Continue with default values (i.e. led off).")

    section_name = 'BluetoothToggleLed'
    led_pin = None
    if section_name in cfg:
        if cfg[section_name].getboolean('enabled', fallback=False):
            led_pin = cfg[section_name].getint('led_pin', fallback=None)
            if not led_pin:
                logger.warning("Could not find 'led_pin' or could not read integer value")
    else:
        logger.debug(f"No section {section_name} found. Defaulting to led_pin = None")

    logger.debug(f"Using LED pin = {led_pin}")
    return led_pin


if __name__ == "__main__":
    if len(sys.argv) == 3:
        logconsole.setLevel(logging.DEBUG)

    if 2 <= len(sys.argv) <= 3:
        cfg_led_pin = get_led_pin_config('../../settings/gpio_settings.ini')
        bt_switch(sys.argv[1], cfg_led_pin)
    else:
        bt_usage(sys.argv[0])
