import logging
import jukebox.cfghandler
import jukebox.plugs as plugin

from .player_status import PlayerStatus
# from .mpd import MpdPlayerBuilder
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

    def get(self, player_name, **kwargs):
        return self.create(player_name, **kwargs)

factory: PlayersFactory


@plugin.initialize
def initialize():
    global players
    player_status = PlayerStatus()
    players = PlayersFactory()
    players.register_builder('Spotify', SpotifyPlayerBuilder(player_status))
    # players.register_builder('MPD', MpdPlayerBuilder())


@plugin.atexit
def atexit(**ignored_kwargs):
    global players
    for player in players.keys():
        players.get(player).exit()


@plugin.register
def play_single(player: str, uri: str):
    """Play a single song"""
    players.get(player).play_single(uri)


# TODO: Currently not implemented for MPD
@plugin.register
def play_playlist(player: str, uri: str):
    """Play a playlist"""
    if player == 'Spotify':
        players.get(player).play_playlist(uri)


@plugin.register
def play_album(player: str, album: str, albumartist: str = None):
    """Play an album"""
    if player == 'MPD':
        if not albumartist:
            return logger.error('Missing arguments for MPD operation, skipping operation')

        return players.get(player).play_album(album, albumartist)

    if player == 'Spotify':
        return players.get(player).play_album(uri = album)


@plugin.register
def play_folder(player: str, folder: str):
    """Play a folder"""
    if player == 'MPD':
        players.get(player).play_folder(folder)


@plugin.register
def play(player: str):
    """Start playing the current song"""
    players.get(player).play()


@plugin.register
def pause(player: str):
    """Pause playback"""
    players.get(player).pause()


@plugin.register
def prev(player: str):
    """Skip to previous track"""
    players.get(player).prev()


@plugin.register
def next(player: str):
    """Skip to next track"""
    players.get(player).next()


@plugin.register
def shuffle(player: str, value: int = -1):
    """Toggle or set shuffle (-1 toggle, 0 no suffle, 1 shuffle)"""
    players.get(player).shuffle(value)


@plugin.register
def repeat(player: str, value: int = -1):
    """Toggle or set repeat (-1 toggle, 0 no repeat, 1 context, 2 single)"""
    players.get(player).repeat(value)


@plugin.register
def seek(player: str, pos: int = 0):
    """Seek to a position of the current song in ms"""
    players.get(player).seek(pos)
