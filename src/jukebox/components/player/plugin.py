"""Player plugin entry point with MPD as the default backend."""

import jukebox.plugs as plugs

from .mpd_plugin import initialize_mpd_player


player_ctrl = None


@plugs.initialize
def initialize():
    global player_ctrl
    player_ctrl = initialize_mpd_player(__name__)


@plugs.atexit
def atexit(**ignored_kwargs):
    return player_ctrl.exit()
