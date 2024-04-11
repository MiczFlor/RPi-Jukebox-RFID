# RPi-Jukebox-RFID Version 3
# Copyright (c) See file LICENSE in project root folder

from jukebox.multitimer import (GenericTimerClass, GenericMultiTimerClass)
import logging
import jukebox.cfghandler
import jukebox.plugs as plugin
from .idle_shutdown_timer import IdleShutdownTimer


logger = logging.getLogger('jb.timers')
cfg = jukebox.cfghandler.get_handler('jukebox')

IDLE_SHUTDOWN_TIMER_MIN_TIMEOUT_SECONDS = 60


# ---------------------------------------------------------------------------
# Action functions for Timers
# ---------------------------------------------------------------------------
def shutdown():
    logger.info("Shutting down on timer request...")
    plugin.call_ignore_errors('host', 'shutdown')


def stop_player():
    logger.info("Stopping the player on timer request...")
    plugin.call_ignore_errors('player', 'ctrl', 'stop')


class VolumeFadeOutActionClass:
    def __init__(self, iterations):
        self.iterations = iterations
        # Get the current volume, calculate step size
        self.volume = plugin.call('volume', 'ctrl', 'get_volume')
        self.step = float(self.volume) / iterations

    def __call__(self, iteration):
        self.volume = self.volume - self.step
        logger.debug(f"Decrease volume to {self.volume} (Iteration index {iteration}/{self.iterations}-1)")
        plugin.call_ignore_errors('volume', 'ctrl', 'set_volume', args=[int(self.volume)])
        if iteration == 0:
            logger.debug("Shut down from volume fade out")
            plugin.call_ignore_errors('host', 'shutdown')


# ---------------------------------------------------------------------------
# Create the timers
# ---------------------------------------------------------------------------
timer_shutdown: GenericTimerClass
timer_stop_player: GenericTimerClass
timer_fade_volume: GenericMultiTimerClass
timer_idle_shutdown: IdleShutdownTimer


@plugin.finalize
def finalize():
    # TODO: Example with how to call the timers from RPC?

    # Create the various timers with fitting doc for plugin reference
    global timer_shutdown
    timeout = cfg.setndefault('timers', 'shutdown', 'default_timeout_sec', value=60 * 60)
    timer_shutdown = GenericTimerClass(f"{plugin.loaded_as(__name__)}.timer_shutdown",
                                       timeout, shutdown)
    timer_shutdown.__doc__ = "Timer for automatic shutdown"
    # Note: Since timer_shutdown is an instance of a class from a different module,
    # auto-registration would register it with that module. Manually set package to this plugin module
    plugin.register(timer_shutdown, name='timer_shutdown', package=plugin.loaded_as(__name__))

    global timer_stop_player
    timeout = cfg.setndefault('timers', 'stop_player', 'default_timeout_sec', value=60 * 60)
    timer_stop_player = GenericTimerClass(f"{plugin.loaded_as(__name__)}.timer_stop_player",
                                          timeout, stop_player)
    timer_stop_player.__doc__ = "Timer for automatic player stop"
    plugin.register(timer_stop_player, name='timer_stop_player', package=plugin.loaded_as(__name__))

    global timer_fade_volume
    timeout = cfg.setndefault('timers', 'volume_fade_out', 'default_time_per_iteration_sec', value=15 * 60)
    steps = cfg.setndefault('timers', 'volume_fade_out', 'number_of_steps', value=10)
    timer_fade_volume = GenericMultiTimerClass(f"{plugin.loaded_as(__name__)}.timer_fade_volume",
                                               steps, timeout, VolumeFadeOutActionClass)
    timer_fade_volume.__doc__ = "Timer step-wise volume fade out and shutdown"
    plugin.register(timer_fade_volume, name='timer_fade_volume', package=plugin.loaded_as(__name__))

    global timer_idle_shutdown
    timeout = cfg.setndefault('timers', 'idle_shutdown', 'timeout_sec', value=0)
    try:
        timeout = int(timeout)
    except ValueError:
        logger.warning(f'invalid timers.idle_shutdown.timeout_sec value {repr(timeout)}')
        timeout = 0
    if timeout < IDLE_SHUTDOWN_TIMER_MIN_TIMEOUT_SECONDS:
        logger.info('disabling idle shutdown timer; set '
                    'timers.idle_shutdown.timeout_sec to at least '
                    f'{IDLE_SHUTDOWN_TIMER_MIN_TIMEOUT_SECONDS} seconds to enable')
        timeout = 0
    if not timeout:
        timer_idle_shutdown = None
    else:
        timer_idle_shutdown = IdleShutdownTimer(timeout)
        timer_idle_shutdown.__doc__ = 'Timer for automatic shutdown on idle'
        timer_idle_shutdown.start()

    # The idle Timer does work in a little sneaky way
    # Idle is when there are no calls through the plugin module
    # Ahh, but also when music is playing this is not idle...
    # Use setattr to replace plugin._call with a plugin._call that saves last access time

    # Three options:
    # (a) whenever a call happens -> restart timer
    # (b) save last call access time -> when timer times out, check that time with timer and restart if necessary with
    # (c) Sniffer on Publisher -> If nothing happens for ages
    #     Most efficient would be a measure the time in the Publisher and use a callback
    # (d) PubSub starts a Timer with target=shutdown. Timer can reset time via function call
    # delta time

    # MPD


@plugin.atexit
def atexit(**ignored_kwargs):
    global timer_shutdown
    timer_shutdown.cancel()
    global timer_stop_player
    timer_stop_player.cancel()
    global timer_fade_volume
    timer_fade_volume.cancel()
    ret = [timer_shutdown.timer_thread, timer_stop_player.timer_thread, timer_fade_volume.timer_thread]
    global timer_idle_shutdown
    if timer_idle_shutdown is not None:
        timer_idle_shutdown.cancel()
        ret += [timer_idle_shutdown]
    return ret
