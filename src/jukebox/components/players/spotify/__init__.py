import logging
import jukebox.cfghandler

from .http_client import SpotifyHttpClient

logger = logging.getLogger('jb.players.spotify')
cfg = jukebox.cfghandler.get_handler('jukebox')

# Spotify Interface
class SpotifyPlayer:
    def __init__(self):
        logger.debug('Init Spotify')
        host = cfg.getn('playerspot', 'host')
        self.http_client = SpotifyHttpClient(host)

    def play_single(self, uri: str):
        play = True
        self.http_client.play_uri(uri, play)


class SpotifyPlayerBuilder:
    def __init__(self):
        self._instance = None

    def __call__(self, **_ignored):
        if not self._instance:
            self._instance = SpotifyPlayer()

        return self._instance
