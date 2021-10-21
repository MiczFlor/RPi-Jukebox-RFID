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

import os
import shutil
import subprocess
import logging
import jukebox.plugs as plugin
import jukebox.cfghandler
import jukebox.publishing
from jukebox.multitimer import GenericEndlessTimerClass

# This is a slightly dirty way of checking if we are on an RPi
# JukeBox installs the dependency RPI which has no meaning on other machines
# It could still be installed, though, and this check will be false positive
try:
    import RPi.gpio as gpio  # noqa: F401
    IS_RPI = True
except ModuleNotFoundError:
    IS_RPI = False


logger = logging.getLogger('jb.host.lnx')
cfg = jukebox.cfghandler.get_handler('jukebox')
# Get the main Thread Publisher
publisher = jukebox.publishing.get_publisher()

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
    debug_flag = '-k' if IS_DEBUG else ''
    # ret = subprocess.run(['sudo', 'shutdown', '-h', 'now'],
    #                      stdout=subprocess.PIPE, stderr=subprocess.STDOUT, check=False)
    # Detach the shell and wait 1 second before command execution
    # for return value to pass up the RPC call stack.
    # The return value has no meaning itself, but the RPC call stack should complete correctly
    # This works on the RPi w/o further authentification, on other machines a systemctl reboot may work better
    # If authentication is required, the command will simply not execute and time out
    ret = subprocess.run(f'(sleep 1; sudo shutdown {debug_flag} -h now) &', shell=True,
                         stdout=subprocess.PIPE, stderr=subprocess.STDOUT, check=False,
                         stdin=subprocess.DEVNULL)
    if ret.returncode != 0:
        logger.error(f"{ret.stdout}")
    if not IS_DEBUG:
        logger.info('Skipping system command due to debug mode')


@plugin.register
def reboot():
    logger.info('Rebooting down host system now')
    debug_flag = '-k' if IS_DEBUG else ''
    ret = subprocess.run(f'(sleep 1; sudo shutdown {debug_flag} -r now) &', shell=True,
                         stdout=subprocess.PIPE, stderr=subprocess.STDOUT, check=False,
                         stdin=subprocess.DEVNULL)
    if ret.returncode != 0:
        logger.error(f"{ret.stdout}")
    if IS_DEBUG:
        logger.info('Reboot command executed in debug mode')


@plugin.register
def jukebox_is_service():
    """Check if current Jukebox process is running as a service"""
    ret = subprocess.run('systemctl show --property MainPID --value jukebox-daemon', shell=True,
                         stdout=subprocess.PIPE, stderr=subprocess.STDOUT, check=False,
                         stdin=subprocess.DEVNULL)
    if ret.returncode != 0:
        msg = f"Error in finding service PID: {ret.stdout}"
        logger.error(msg)

    if ret.stdout != os.getpid():
        return False
    else:
        return True


@plugin.register
def restart_service():
    """Restart Jukebox App if running as a service"""
    msg = ''
    if not jukebox_is_service():
        msg = "I am not running as a service! Doing nothing"
    else:
        ret = subprocess.run('(sleep 1; sudo systemctl restart jukebox-daemon.service) &',
                             stdout=subprocess.PIPE, stderr=subprocess.STDOUT, check=False,
                             stdin=subprocess.DEVNULL)
        if ret.returncode != 0:
            msg = f"Error in restarting service: {ret.stdout}"
    if not msg:
        msg = 'Restart service request dispatched successfully to host'
    logger.info(msg)
    return msg


@plugin.register()
def get_disk_usage(path='/'):
    """Return the disk usage in Megabytes as dictionary for RPC export"""
    [t, u, f] = shutil.disk_usage(path)
    return {'total': round(t / 1024 / 1024), 'used': round(u / 1024 / 1024), 'free': round(f / 1024 / 1024)}


# ---------------------------------------------------------------------------
# Temperature
# ---------------------------------------------------------------------------
timer_temperature: GenericEndlessTimerClass


@plugin.register
def get_cpu_temperature():
    """Get the CPU temperature with single decimal point

    No error handling: this is expected to take place up-level!"""
    with open('/sys/class/thermal/thermal_zone0/temp') as f:
        temperature = float(f.readline()) / 1000.0
        temperature = round(temperature, 1)
    return temperature


@plugin.register
def publish_cpu_temperature():
    global timer_temperature
    try:
        temperature = get_cpu_temperature()
    except Exception as e:
        logger.error(f"Error reading temperature. Canceling temperature publisher. {e.__class__.__name__}: {e}")
        # If there was an error reading the temperature, the is no sense in keeping the timer alive and running
        # into the same problem again
        timer_temperature.cancel()
        # Revoke Temperature from publisher
        publisher.revoke('host.temperature.cpu')
    else:
        # May be called from different threads: get thread-correct publisher instance
        jukebox.publishing.get_publisher().send('host.temperature.cpu', str(temperature))


# ---------------------------------------------------------------------------
# MISC
# ---------------------------------------------------------------------------
@plugin.register()
def wlan_disable_power_down(card=None):
    """Turn off power management of wlan. Keep RPi reachable via WLAN

    This must be done after every reboot
    card=None takes card from configuration file"""
    if card is None:
        card = cfg.setndefault('host', 'wlan_power', 'card', default='wlan0')
    logger.info(f'Disable power down management of {card}')
    ret = subprocess.run(['sudo', 'iwconfig', card, 'power', 'off'],
                         stdout=subprocess.PIPE, stderr=subprocess.STDOUT, check=False)
    if ret.returncode != 0:
        logger.error(f"{ret.stdout}")


@plugin.initialize
def initialize():
    wlan_power = cfg.setndefault('host', 'wlan_power', 'disable_power_down', value=True)
    card = cfg.setndefault('host', 'wlan_power', 'card', value='wlan0')
    if wlan_power:
        wlan_disable_power_down(card)


@plugin.finalize
def finalize():
    global timer_temperature
    enabled = cfg.setndefault('host', 'publish_temperature', 'enabled', value=True)
    wait_time = cfg.setndefault('host', 'publish_temperature', 'timer_interval_sec', value=5)
    timer_temperature = GenericEndlessTimerClass('host.timer.cputemp', wait_time, publish_cpu_temperature)
    timer_temperature.__doc__ = "Endless timer for publishing CPU temperature"
    # Note: Since timer_temperature is an instance of a class from a different module,
    # auto-registration would register it with that module. Manually set package to this plugin module
    plugin.register(timer_temperature, name='timer_temperature', package=plugin.loaded_as(__name__))
    if enabled:
        publish_cpu_temperature()
        timer_temperature.start()


@plugin.atexit
def atexit(**ignored_kwargs):
    global timer_temperature
    timer_temperature.cancel()


# ---------------------------------------------------------------------------
# RPi-only stuff
# ---------------------------------------------------------------------------
if IS_RPI:

    @plugin.register
    def hdmi_power_down():
        """Power down HDMI circuits to save power if no display is connected

        This must be done after every reboot"""
        logger.info('Power down HDMI circuits')
        ret = subprocess.run(['sudo', '/usr/bin/tvservice', '-o'],
                             stdout=subprocess.PIPE, stderr=subprocess.STDOUT, check=False)
        if ret.returncode != 0:
            logger.error(f"{ret.stdout}")

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

    @plugin.initialize
    def rpi_initialize():
        hdmi_off = cfg.setndefault('host', 'rpi', 'hdmi_power_down', default=False)
        if hdmi_off:
            hdmi_power_down()
