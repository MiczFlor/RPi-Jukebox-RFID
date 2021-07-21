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
    """Play the jingle using the configured jingle service"""
    global factory
    factory.auto(filename).play(filename)


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
        plugin.call_ignore_errors('jingle', 'play_startup', as_thread=True)
    else:
        logger.debug("No startup sound in config file")


@plugin.atexit
def atexit(esignal: int):
    # Only play the shutdown sound when terminated with a proper command. Not on Ctrl-C (faster exit for developers :-)
    if esignal == signal.SIGTERM:
        if 'shutdown_sound' in cfg['jingle']:
            # Currently cannot start playing in separate thread, as jukebox.exit_handler has no way of knowing that it
            # should wait for this thread. So for now just play it in calling thread
            # plugin.call_ignore_errors('jingle', 'play_shutdown', as_thread=True)
            play_shutdown()
        else:
            logger.debug("No shutdown sound in config file")
