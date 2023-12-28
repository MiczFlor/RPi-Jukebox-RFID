# RPi-Jukebox-RFID Version 3
# Copyright (c) See file LICENSE in project root folder
"""
Jingle Playback Factory for extensible run-time support of various file types
"""

import os.path
import signal
import logging
import jukebox.plugs as plugin
import jukebox.cfghandler

logger = logging.getLogger('jb.jingle')
cfg = jukebox.cfghandler.get_handler('jukebox')


class JingleFactory:
    """Jingle Factory"""

    def __init__(self):
        self._builders = {}

    def register(self, key, builder):
        logger.debug(f"Register '{key}' in {self.__class__}.")
        self._builders[key] = builder

    def get(self, key):
        return self._builders.get(key)()

    def list(self):
        """List the available volume services"""
        return self._builders.keys()

    def auto(self, filename):
        # Check the config if the user has a specific config
        # else use auto resolver function
        key = cfg['jingle'].get('service', 'auto')
        if key == 'auto':
            # This is a very simple resolving function based on file extension
            # This does no allow for duplicate entries etc...
            key = os.path.splitext(filename)[1][1:]
        logger.debug(f"Auto: '{key}' from {filename}.")
        return self.get(key)


factory: JingleFactory


@plugin.initialize
def initialize():
    global factory
    factory = JingleFactory()


@plugin.register
def play(filename):
    """Play the jingle using the configured jingle service

    > [!NOTE]
    > This runs in a separate thread. And this may cause troubles
    > when changing the volume level before
    > and after the sound playback: There is nothing to prevent another
    > thread from changing the volume and sink while playback happens
    > and afterwards we change the volume back to where it was before!

    There is no way around this dilemma except for not running the jingle as a
    separate thread. Currently (as thread) even the RPC is started before the sound
    is finished and the volume is reset to normal...

    However: Volume plugin is loaded before jingle and sets the default
    volume. No interference here. It can now only happen
    if (a) through the RPC or (b) some other plugin the volume is changed. Okay, now
    (a) let's hope that there is enough delay in the user requesting a volume change
    (b) let's hope no other plugin wants to do that
    (c) no bluetooth device connects during this time (and pulseaudio control is set to toggle_on_connect)
    and take our changes with the threaded approach.
    """
    global factory
    jingle_volume = cfg.getn('jingle', 'volume', default=None)
    active_volume = None
    if jingle_volume is not None:
        active_volume = plugin.call_ignore_errors('volume', 'ctrl', 'get_volume')
        plugin.call_ignore_errors('volume', 'ctrl', 'set_volume', args=[jingle_volume])
    factory.auto(filename).play(filename)
    if jingle_volume is not None:
        plugin.call_ignore_errors('volume', 'ctrl', 'set_volume', args=[active_volume])


@plugin.register
def play_startup():
    """Play the startup sound (using jingle.play)"""
    play(cfg['jingle']['startup_sound'])


@plugin.register
def play_shutdown():
    """Play the shutdown sound (using jingle.play)"""
    play(cfg['jingle']['shutdown_sound'])


@plugin.finalize
def finalize():
    if 'startup_sound' in cfg['jingle']:
        plugin.call_ignore_errors('jingle', 'play_startup', as_thread=True, thread_name='StartJingle')
    else:
        logger.debug("No startup sound in config file")


@plugin.atexit
def atexit(signal_id: int, **ignored_kwargs):
    # Only play the shutdown sound when terminated with a proper command. Not on Ctrl-C (faster exit for developers :-)
    if signal_id == signal.SIGTERM:
        if 'shutdown_sound' in cfg['jingle']:
            # Never play the shutdown sound as thread!
            # It causes a race condition with the plugin volume, which shuts down faster
            # But we need to have the plugin volume to reset the volume level after the sound was played
            plugin.call_ignore_errors('jingle', 'play_shutdown', as_thread=False)
        else:
            logger.debug("No shutdown sound in config file")
