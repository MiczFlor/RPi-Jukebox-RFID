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
Volume Control Factory for run-time switching of volume control plugin
"""
import logging
import jukebox.plugs as plugin
import jukebox.cfghandler

logger = logging.getLogger('jb.volume')
cfg = jukebox.cfghandler.get_handler('jukebox')


@plugin.register
class VolumeFactory:
    """Volume Factory"""

    def __init__(self):
        self._builders = {}
        self._active_key = None

    def register(self, key, builder):
        logger.debug(f"Register '{key}' in {self.__class__}")
        self._builders[key] = builder

    def get(self, key):
        return self._builders.get(key)()

    @plugin.tag
    def list(self):
        """List the available volume services"""
        return self._builders.keys()

    @plugin.tag
    def set_active(self, key):
        """Set the active volume service which gets registered as 'ctrl'"""
        logger.debug(f"Set active '{key}' in VolumeFactory")
        if self._builders.get(key) is None:
            logger.error(f"Ignoring activation request for unknown volume service key: '{key}'")
            return
        plugin.register(self.get(key), package="volume", name="ctrl", replace=True)
        self._active_key = key

    @plugin.tag
    def get_active(self):
        return self._active_key


factory: VolumeFactory


@plugin.initialize
def initialize():
    global factory
    logger.debug("Initialize volume factory")
    factory = VolumeFactory(plugin_name='factory')


@plugin.finalize
def finalize():
    global factory
    logger.debug("Finalize volume factory set up")
    interface_name = cfg.getn('volume', 'interface', default=None)
    if interface_name is not None:
        factory.set_active(interface_name)
        startup_volume = cfg.getn('volume', 'startup_volume', default=None)
        if startup_volume is not None:
            plugin.call_ignore_errors('volume', 'ctrl', 'set_volume', args=[startup_volume])
        max_volume = cfg.getn('volume', 'max_volume', default=None)
        if max_volume is not None:
            plugin.call_ignore_errors('volume', 'ctrl', 'set_max_volume', args=[max_volume])
