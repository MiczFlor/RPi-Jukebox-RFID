import os.path
import logging
import subprocess
import jukebox.plugin as plugin
import jukebox.cfghandler

logger = logging.getLogger('jb.jingle')
cfg = jukebox.cfghandler.get_handler('jukebox')


class JingleFactory:

    def __init__(self):
        self._builders = {}

    def register(self, key, builder):
        logger.debug(f"Register '{key}' in {self.__class__}.")
        self._builders[key] = builder

    def get(self, key):
        return self._builders.get(key)()

    def list(self):
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


factory = JingleFactory()


@plugin.register
def play(filename):
    global factory
    factory.auto(filename).play(filename)


@plugin.register
def play_startup():
    play(cfg['jingle']['startup_sound'])


@plugin.register
def play_shutdown():
    play(cfg['jingle']['shutdown_sound'])


# ---------------------------------------------------------------------------
# MP3 Jingle Service
# ---------------------------------------------------------------------------
# A generic mp3 player service for the jingle playback

@plugin.register(auto_tag=True)
class JingleMp3Play:

    def play(self, filename):
        subargs = cfg['jingle'].get('call_parameters', [])
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
        self._instance = JingleMp3Play(plugin_name='mp3jingle', plugin_register=True)

    def __call__(self, *args, **kwargs):
        return self._instance


factory.register("mp3", JingleMp3PlayBuilder())
