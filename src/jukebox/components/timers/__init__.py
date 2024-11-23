# RPi-Jukebox-RFID Version 3
# Copyright (c) See file LICENSE in project root folder

import logging
import jukebox.cfghandler
import jukebox.plugs as plugin
from jukebox.multitimer import GenericTimerClass
from .idle_shutdown_timer import IdleShutdownTimer
from .volume_fadeout_shutdown_timer import VolumeFadoutAndShutdown


logger = logging.getLogger('jb.timers')
cfg = jukebox.cfghandler.get_handler('jukebox')


# ---------------------------------------------------------------------------
# Action functions for Timers
# ---------------------------------------------------------------------------
def shutdown():
    logger.info("Shutting down on timer request...")
    plugin.call_ignore_errors('host', 'shutdown')


def stop_player():
    logger.info("Stopping the player on timer request...")
    plugin.call_ignore_errors('player', 'ctrl', 'stop')


# ---------------------------------------------------------------------------
# Create the timers
# ---------------------------------------------------------------------------
timer_shutdown: GenericTimerClass
timer_stop_player: GenericTimerClass
timer_fade_volume: VolumeFadoutAndShutdown
timer_idle_shutdown: IdleShutdownTimer


@plugin.finalize
def finalize():
    # Shutdown Timer
    global timer_shutdown
    timeout = cfg.setndefault('timers', 'shutdown', 'default_timeout_sec', value=60 * 60)
    timer_shutdown = GenericTimerClass(f"{plugin.loaded_as(__name__)}.timer_shutdown",
                                       timeout, shutdown)
    timer_shutdown.__doc__ = "Timer for automatic shutdown"
    # Note: Since timer_shutdown is an instance of a class from a different module,
    # auto-registration would register it with that module. Manually set package to this plugin module
    plugin.register(timer_shutdown, name='timer_shutdown', package=plugin.loaded_as(__name__))

    # Stop Playback Timer
    global timer_stop_player
    timeout = cfg.setndefault('timers', 'stop_player', 'default_timeout_sec', value=60 * 60)
    timer_stop_player = GenericTimerClass(f"{plugin.loaded_as(__name__)}.timer_stop_player",
                                          timeout, stop_player)
    timer_stop_player.__doc__ = "Timer for automatic player stop"
    plugin.register(timer_stop_player, name='timer_stop_player', package=plugin.loaded_as(__name__))

    # Volume Fadeout and Shutdown Timer
    timer_fade_volume = VolumeFadoutAndShutdown(
        name=f"{plugin.loaded_as(__name__)}.timer_fade_volume"
    )
    plugin.register(timer_fade_volume, name='timer_fade_volume', package=plugin.loaded_as(__name__))

    # Idle Timer
    global timer_idle_shutdown
    idle_timeout = cfg.setndefault('timers', 'idle_shutdown', 'timeout_sec', value=0)
    timer_idle_shutdown = IdleShutdownTimer(package=plugin.loaded_as(__name__), idle_timeout=idle_timeout)
    plugin.register(timer_idle_shutdown, name='timer_idle_shutdown', package=plugin.loaded_as(__name__))

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
    global timer_idle_shutdown
    timer_idle_shutdown.cancel()
    global timer_idle_check
    timer_idle_check.cancel()
    ret = [
        timer_shutdown.timer_thread,
        timer_stop_player.timer_thread,
        timer_fade_volume.timer_thread,
        timer_idle_shutdown.timer_thread,
        timer_idle_check.timer_thread
    ]
    return ret
