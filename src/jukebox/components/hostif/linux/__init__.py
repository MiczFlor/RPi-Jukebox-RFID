# MIT License
#
# Copyright (c) 2021 Christian Banz
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#
# Contributing author(s):
# - Christian Banz

from jukebox.multitimer import GenericEndlessTimerClass
import subprocess
import logging
import jukebox.plugs as plugin
import jukebox.cfghandler
from typing import Any

# This is a slightly dirty way of checking if we are on an RPi
# JukeBox installs the dependency RPI which has no meaning on other machines
try:
    import RPi.gpio as gpio
    IS_RPI = True
except ModuleNotFoundError:
    IS_RPI = False


logger = logging.getLogger('jb.host.lnx')
cfg = jukebox.cfghandler.get_handler('jukebox')

# In debug mode, shutdown and reboot command are not actually executed
IS_DEBUG = False
try:
    IS_DEBUG = cfg.setndefault('host', 'debug_mode', value=False)
except Exception:
    pass


# ---------------------------------------------------------------------------
# Shutdown / Reboot
# ---------------------------------------------------------------------------
@plugin.register
def shutdown():
    logger.info('Shutting down host system now')
    if not IS_DEBUG:
        ret = subprocess.run(['sudo', 'shutdown', '-h', 'now'],
                             stdout=subprocess.PIPE, stderr=subprocess.STDOUT, check=False)
        if ret.returncode != 0:
            logger.error(f"{ret.stdout}")
    else:
        logger.info('Skipping system command due to debug mode')


@plugin.register
def reboot():
    logger.info('Rebooting down host system now')
    if not IS_DEBUG:
        ret = subprocess.run(['sudo', 'reboot'],
                             stdout=subprocess.PIPE, stderr=subprocess.STDOUT, check=False)
        if ret.returncode != 0:
            logger.error(f"{ret.stdout}")
    else:
        logger.info('Skipping system command due to debug mode')


# ---------------------------------------------------------------------------
# Temperature
# ---------------------------------------------------------------------------
timer_temperature: Any


@plugin.register
def get_cpu_temperature():
    """Get the CPU temperature with single decimal point

    No error handling: this is expected to take place up-level!"""
    with open('/sys/class/thermal/thermal_zone0/temp') as f:
        temperature = float(f.readline()) / 1000.0
        temperature = round(temperature, 1)
    return temperature


@plugin.register
def publish_cpu_temperature(**ignored_kwargs):
    global timer_temperature
    try:
        temperature = get_cpu_temperature()
    except Exception as e:
        logger.error(f"Error reading temperature. Canceling temperature publisher. {e.__class__.__name__}: {e}")
        # If there was an error reading the temperature, the is no sense in keepin the timer alive and running
        # into the same problem again
        timer_temperature.cancel()
        temperature = '0.0'
    # TODO: Send to pubsub
    logger.debug(f'Publishing Temperature: {temperature}')


@plugin.finalize
def temperature_finalize():
    global timer_temperature
    enabled = cfg.setndefault('host', 'publish_temperature', 'enabled', value=True)
    wait_time = cfg.setndefault('host', 'publish_temperature', 'timer_interval_sec', value=5)
    timer_temperature = GenericEndlessTimerClass(wait_time, publish_cpu_temperature)
    timer_temperature.__doc__ = "Endless timer for publishing CPU temperature"
    timer_temperature.name = 'TimeCpuTemp'
    # Note: Since timer_temperature is an instance of a class from a different module,
    # auto-registration would register it with that module. Manually set package to this plugin module
    plugin.register(timer_temperature, name='timer_temperature', package=plugin.loaded_as(__name__))
    if enabled:
        timer_temperature.start()


@plugin.atexit
def temperature_atexit(**ignored_kwargs):
    global timer_temperature
    timer_temperature.cancel()


# ---------------------------------------------------------------------------
# RPi-only stuff
# ---------------------------------------------------------------------------
if IS_RPI:

    @plugin.register
    def get_throttled():
        # https://www.raspberrypi.org/documentation/computers/os.html#get_throttled
        ret = subprocess.run(['sudo', 'vcgencmd', 'get_throttled'],
                             stdout=subprocess.PIPE, check=False)
        status = int(ret.stdout)
        # Decode the bit array
        # TODO: Decode all error values into strings
        if status == 0:
            status_string = "OK"
        else:
            status_string = f"Not OK (Code: {ret.status})"
        return status_string
