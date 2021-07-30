"""
Generic MP3 jingle Service for jingle.JingleFactory
"""
import logging
import subprocess
import jukebox.plugs as plugin
import jukebox.cfghandler

logger = logging.getLogger('jb.jingle.mp3')
cfg = jukebox.cfghandler.get_handler('jukebox')


# ---------------------------------------------------------------------------
# MP3 Jingle Service
# ---------------------------------------------------------------------------
# A generic mp3 player service for the jingle playback

@plugin.register(auto_tag=True)
class JingleMp3Play:
    """Jingle Service for playing MP3 files"""

    def play(self, filename):
        """Play the MP3 file"""
        subargs = cfg.getn('jinglemp3', 'call_parameters', default=[])
        res = subprocess.run(['mpg123', '-q', *subargs, filename], capture_output=True)
        if res.stderr != b'':
            logger.error(f"Playing MP3: {res.stderr}")


class JingleMp3PlayBuilder:

    def __init__(self):
        """
        Builder instantiates JingleMp3Play during init and not during first call because
        we want JingleMp3Play registers as plugin function in any case if this plugin is loaded
        (and not only on first use!)
        """
        self._instance = JingleMp3Play(plugin_name='jinglemp3', plugin_register=True)

    def __call__(self, *args, **kwargs):
        return self._instance


# ---------------------------------------------------------------------------
# Plugin Initializer / Finalizer
# ---------------------------------------------------------------------------

@plugin.initialize
def initialize():
    jingle = plugin.get('jingle')
    jingle.factory.register("mp3", JingleMp3PlayBuilder())
