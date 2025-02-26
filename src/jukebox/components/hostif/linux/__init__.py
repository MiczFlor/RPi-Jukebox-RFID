# RPi-Jukebox-RFID Version 3
# Copyright (c) See file LICENSE in project root folder

import os
import shutil
import subprocess
import logging
import jukebox.plugs as plugin
import jukebox.cfghandler
import jukebox.publishing
import jukebox.speaking_text
from jukebox.multitimer import GenericEndlessTimerClass

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
    """Shutdown the host machine"""
    logger.info('Shutting down host system now')
    debug_flag = '-k' if IS_DEBUG else ''
    # Detach the shell and wait 1 second before command execution
    # for return value to pass up the RPC call stack.
    # The return value has no meaning itself, but the RPC call stack should complete correctly
    # In order to really detach the shell command, we also need to detach the pipes for outputs
    # If omit that, there is a dead lock and the service will not shut down properly
    # This works on the RPi w/o further authentication, on other machines a systemctl reboot may work better
    # If authentication is required, the command will simply not execute and time out
    ret = subprocess.run(f'(sleep 1; sudo shutdown {debug_flag} -h now) &', shell=True, capture_output=False,
                         stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=False,
                         stdin=subprocess.DEVNULL)
    if ret.returncode != 0:
        logger.error(f"{ret.stdout}")
    if IS_DEBUG:
        logger.info('Skipping system command due to debug mode')
    logger.info('Shutdown command dispatched to host')


@plugin.register
def reboot():
    """Reboot the host machine"""
    logger.info('Rebooting down host system now')
    debug_flag = '-k' if IS_DEBUG else ''
    ret = subprocess.run(f'(sleep 1; sudo shutdown {debug_flag} -r now) &', shell=True, capture_output=False,
                         stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=False,
                         stdin=subprocess.DEVNULL)
    if ret.returncode != 0:
        logger.error(f"{ret.stdout}")
    if IS_DEBUG:
        logger.info('Reboot command skipped due to debug mode')
    logger.info('Reboot command dispatched to host')


@plugin.register
def jukebox_is_service():
    """Check if current Jukebox process is running as a service"""
    ret = subprocess.run(['systemctl', 'show', '--user', '--property', 'MainPID', '--value', 'jukebox-daemon'],
                         stdout=subprocess.PIPE, stderr=subprocess.STDOUT, check=False,
                         stdin=subprocess.DEVNULL)
    if ret.returncode != 0:
        msg = f"Error in finding service PID: {ret.stdout}"
        logger.error(msg)
        pid = 0
    else:
        try:
            pid = int(ret.stdout.decode().strip())
        except Exception as e:
            logger.error(f"{e.__class__.__name__}: {e}")
            pid = 0

    return pid == os.getpid()


@plugin.register
def is_any_jukebox_service_active():
    """Check if a Jukebox service is running

    > [!NOTE]
    > Does not have the be the current app, that is running as a service!
    """
    ret = subprocess.run(["systemctl", "--user", "show", "jukebox-daemon", "--property", "ActiveState", "--value"],
                         stdout=subprocess.PIPE, stderr=subprocess.STDOUT, check=False,
                         stdin=subprocess.DEVNULL)
    if ret.returncode != 0:
        logger.error(f"Error in finding service state: {ret.stdout}")
        is_active = False
    else:
        try:
            is_active = ret.stdout.decode().strip() == 'active'
        except Exception as e:
            logger.error(f"{e.__class__.__name__}: {e}")
            is_active = False
    return is_active


@plugin.register
def restart_service():
    """Restart Jukebox App if running as a service"""
    msg = ''
    if not jukebox_is_service():
        msg = "I am not running as a service! Doing nothing"
    else:
        ret = subprocess.run('(sleep 1; systemctl --user restart jukebox-daemon.service) &', shell=True, capture_output=False,
                             stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=False,
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
# Network
# ---------------------------------------------------------------------------

@plugin.register
def get_ip_address():
    """
    Get the IP address
    """
    p = subprocess.run(['hostname', '-I'], capture_output=True)
    if p.returncode == 0:
        ip_address = p.stdout.strip().decode()
    else:
        ip_address = '127.0.0.1'

    # only get first if multiple adresses are present (ipv4/ipv6)
    ip_address = ip_address.split(' ')[0]
    return ip_address


@plugin.register
def say_my_ip(option='full'):
    ip_address = get_ip_address()

    if option == 'short':
        ip_address = ip_address.split('.')[3]

    ip_address = ip_address.replace('.', '. ')

    jukebox.speaking_text.say(ip_address)


# ---------------------------------------------------------------------------
# MISC
# ---------------------------------------------------------------------------
@plugin.register()
def wlan_disable_power_down(card=None):
    """Turn off power management of wlan. Keep RPi reachable via WLAN

    This must be done after every reboot
    card=None takes card from configuration file"""
    if card is None:
        card = cfg.setndefault('host', 'wlan_power', 'card', value='wlan0')
    logger.info(f'Disable power down management of {card}')
    ret = subprocess.run(['sudo', 'iwconfig', card, 'power', 'off'],
                         stdout=subprocess.PIPE, stderr=subprocess.STDOUT, check=False)
    if ret.returncode != 0:
        logger.error(f"{ret.stdout}")


@plugin.register
def get_autohotspot_status():
    """Get the status of the auto hotspot feature"""
    status = 'not-installed'

    if os.path.isfile("/etc/systemd/system/autohotspot.service"):
        status = 'inactive'

        ret = subprocess.run(['systemctl', 'is-active', 'autohotspot.timer'],
                            stdout=subprocess.PIPE, stderr=subprocess.STDOUT, check=False,
                            stdin=subprocess.DEVNULL)
        # 0 = active, 3 = inactive
        if ret.returncode == 0 or ret.returncode == 3:
            try:
                status = ret.stdout.decode().strip()
            except Exception as e:
                logger.error(f"{e.__class__.__name__}: {e}")
                return {'error': {'code': -1, 'message': e}}
        else:
            msg = f"Error 'get_autohotspot_status': {ret.stdout} (Code: {ret.returncode})"
            logger.error(msg)
            return {'error': {'code': -1, 'message': msg}}

    return status


@plugin.register()
def stop_autohotspot():
    """Stop auto hotspot functionality

    Stopping and disabling the timer and running the service one last time manually
    """
    if os.path.isfile("/etc/systemd/system/autohotspot.service"):
        # Stop timer
        subprocess.run(['sudo', '/usr/bin/systemctl', 'stop', 'autohotspot.timer'],
                        stdout=subprocess.PIPE, stderr=subprocess.STDOUT, check=False)
        # Prevent start after system restart
        subprocess.run(['sudo', '/usr/bin/systemctl', 'disable', 'autohotspot.timer'],
                        stdout=subprocess.PIPE, stderr=subprocess.STDOUT, check=False)
        # Prevent start after system restart (should always be disabled, but make sure)
        subprocess.run(['sudo', '/usr/bin/systemctl', 'disable', 'autohotspot.service'],
                        stdout=subprocess.PIPE, stderr=subprocess.STDOUT, check=False)

        subprocess.run(['sudo', '/usr/bin/systemctl', 'start', 'autohotspot.service'],
                        stdout=subprocess.PIPE, stderr=subprocess.STDOUT, check=False)

        return 'inactive'
    else:
        logger.info("Skipping since no autohotspot functionality is installed.")
        return 'not-installed'


@plugin.register()
def start_autohotspot():
    """Start auto hotspot functionality

    Enabling and starting the timer (timer will start the service)
    """
    if os.path.isfile("/etc/systemd/system/autohotspot.service"):
        # Enable start after system restart
        subprocess.run(['sudo', '/usr/bin/systemctl', 'enable', 'autohotspot.timer'],
                        stdout=subprocess.PIPE, stderr=subprocess.STDOUT, check=False)
        # Start timer (starts the service immediately)
        subprocess.run(['sudo', '/usr/bin/systemctl', 'start', 'autohotspot.timer'],
                        stdout=subprocess.PIPE, stderr=subprocess.STDOUT, check=False)

        return 'active'
    else:
        logger.info("Skipping since no autohotspot functionality is installed.")
        return 'not-installed'


# ---------------------------------------------------------------------------
# RPi-only stuff
# ---------------------------------------------------------------------------
THROTTLE_CODES = {
    0x1: "under-voltage detected",
    0x2: "ARM frequency capped",
    0x4: "currently throttled",
    0x8: "soft temperature limit active",
    0x10000: "under-voltage has occurred",
    0x20000: "ARM frequency capped has occurred",
    0x40000: "throttling has occurred",
    0x80000: "soft temperature limit has occurred"
}


def command_exists(command):
    ret = shutil.which(command)
    return ret is not None


@plugin.register
def hdmi_power_down():
    """Power down HDMI circuits to save power if no display is connected

    This must be done after every reboot"""
    success = False
    commandname = "tvservice"
    if command_exists(commandname):
        logger.info('Power down HDMI circuits')
        ret = subprocess.run(['sudo', commandname, '-o'],
                            stdout=subprocess.PIPE, stderr=subprocess.STDOUT, check=False)
        if ret.returncode != 0:
            logger.error(f"{ret.stdout}")
        else:
            success = True
    else:
        logger.info('Power down HDMI not available on this system')

    return success


def filter_throttle_codes(code):
    for error, msg in THROTTLE_CODES.items():
        if code & error > 0:
            yield msg


@plugin.register
def get_throttled():
    commandname = "vcgencmd"
    if command_exists(commandname):
        # https://www.raspberrypi.org/documentation/computers/os.html#get_throttled
        ret = subprocess.run(['sudo', commandname, 'get_throttled'],
                            stdout=subprocess.PIPE, check=False)
        if ret.returncode != 0:
            status_string = f"Error in subprocess with code: {ret.returncode}"
            logger.error(status_string)
        else:
            try:
                status_code = int(ret.stdout.decode().strip().split('0x')[1], base=16)
            except Exception as e:
                status_string = f"Error in interpreting return value: {e.__class__.__name__}: {e}"
                logger.error(status_string)
            else:
                if status_code == 0:
                    status_string = "All OK - not throttled"
                else:
                    # Decode the bit array after we have handled all the possible exceptions
                    status_string = "Warning: " + ', '.join(filter_throttle_codes(status_code))
    else:
        logger.info('Throttled state not available on this system')
        status_string = "Not available"

    return status_string


# ---------------------------------------------------------------------------
# Init
# ---------------------------------------------------------------------------
@plugin.initialize
def initialize():
    wlan_power = cfg.setndefault('host', 'wlan_power', 'disable_power_down', value=True)
    card = cfg.setndefault('host', 'wlan_power', 'card', value='wlan0')
    if wlan_power:
        wlan_disable_power_down(card)
    hdmi_off = cfg.setndefault('host', 'rpi', 'hdmi_power_down', value=False)
    if hdmi_off:
        hdmi_power_down()


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
    return timer_temperature.timer_thread
