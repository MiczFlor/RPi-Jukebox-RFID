import logging
import jukebox.cfghandler
import jukebox.plugs as plugin

from .mpd import MpdPlayerBuilder
from .spotify import SpotifyPlayerBuilder

logger = logging.getLogger('jb.players')
cfg = jukebox.cfghandler.get_handler('jukebox')


class PlayersFactory:
    def __init__(self):
        self._builders = {}

    def register_builder(self, key, builder):
        self._builders[key] = builder

    def create(self, key, **kwargs):
        builder = self._builders.get(key)
        if not builder:
            raise ValueError(key)
        return builder(**kwargs)

factory: PlayersFactory


@plugin.initialize
def initialize():
    global players
    players = PlayersFactory()
    players.register_builder('Spotify', SpotifyPlayerBuilder)
    players.register_builder('MPD', MpdPlayerBuilder)


@plugin.register
def play_single(player: str, uri: str):
    players.get(player).play_single(uri)
