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

    Note: This runs in a separate thread. And this may cause troubles
    when changing the volume ctrl interface and volume level before
    and after the sound playback: There is nothing to prevent another
    thread from changing the active factory while playback happens
    and afterwards we change it back to where it was before!

    There is no way around this dilemma except for not running the jingle as a
    separate thread. Currently (as thread) even the RPC is started before the sound
    is finished and the volume is reset to normal...

    However: Volume plugin is loaded before jingle and sets the default
    volume. No interference here. It can now only happen
    if (a) through the RPC or (b) some other plugin the volume is changed. Okay, now
    (a) let's hope that there is enough delay in the user requesting a volume change
    (b) let's hope no other plugin wants to do that
    and take our changes with the threaded approach.

    Also note that the MPD plugin starts while the jingle is still playing and starts polling and publishing
    the volume through the current volume service immediately. But in a way that is correct, as this reflects
    the current volume before going back to startup volume
    """
    global factory
    jingle_volume = cfg.getn('jingle', 'volume', default=None)
    active_if = None
    active_volume = None
    if jingle_volume is not None:
        # Change to alsa volume ctrl manager for jingle
        # as this is not played back using MPD
        active_if = plugin.call('volume', 'factory', 'get_active')
        plugin.call('volume', 'factory', 'set_active', args=['alsa'])
        active_volume = plugin.call_ignore_errors('volume', 'ctrl', 'get_volume')
        plugin.call_ignore_errors('volume', 'ctrl', 'set_volume', args=[jingle_volume])
    factory.auto(filename).play(filename)
    if jingle_volume is not None:
        plugin.call_ignore_errors('volume', 'ctrl', 'set_volume', args=[active_volume])
        plugin.call('volume', 'factory', 'set_active', args=[active_if])


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
            return plugin.call_ignore_errors('jingle', 'play_shutdown', as_thread=True, thread_name='ShutdownSound')
        else:
            logger.debug("No shutdown sound in config file")
