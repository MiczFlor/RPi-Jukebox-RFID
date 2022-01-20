import logging
import jukebox.cfghandler

from .http_client import SpotifyHttpClient
from .ws_client import SpotifyWsClient

logger = logging.getLogger('jb.players.spotify')
cfg = jukebox.cfghandler.get_handler('jukebox')

# Spotify Interface
class SpotifyPlayer:
    def __init__(self, player_status):
        logger.debug('Init Spotify')
        host = cfg.getn('playerspot', 'host')
        self.player_status = player_status

        self.http_client = SpotifyHttpClient(host)

        self.ws_client = SpotifyWsClient(
            host = host,
            player_status = self.player_status
        )
        self.ws_client.connect()

    def exit(self):
        logger.debug('Exiting Spotify ...')
        self.http_client.close()
        self.ws_client.close()


    # TODO: Stop playout after the song
    # Spotify would continue automatically
    def play_single(self, uri: str):
        if not uri.startswith('spotify:track:'):
            return logger.error('Provided URI does not match a single track')

        self.http_client.play_uri(uri)


    def play_album(self, uri: str):
        if not uri.startswith('spotify:album:'):
            return logger.error('Provided ID does not match an album URI')

        self.http_client.play_uri(uri)


    def play_playlist(self, uri: str):
        if not uri.startswith('spotify:playlist:'):
            return logger.error('Provided URI does not match a playlist')

        self.http_client.play_uri(uri)


    def play(self):
        self.http_client.play()


    def pause(self):
        self.http_client.pause()


    def prev(self):
        self.http_client.prev()


    def next(self):
        self.http_client.next()


    def shuffle(self, value: int = -1):
        if value > -1:
            return self.http_client.shuffle(value)
        # TODO: Get status first and determine current shuffle state
        # else:
        #     return self.http_client.shuffle(value)

    def repeat(self, value: int = -1):
        if value == 0:
            state = 'none'
        elif value == 1:
            state = 'context'
        elif value == 2:
            state = 'track'
        else:
            # TODO: Get status first and determine current repeat state
            state = 'none'

        return self.http_client.repeat(value)


class SpotifyPlayerBuilder:
    def __init__(self, player_status):
        self._instance = None
        self._player_status = player_status

    def __call__(self, **_ignored):
        if not self._instance:
            self._instance = SpotifyPlayer(self._player_status)

        return self._instance
