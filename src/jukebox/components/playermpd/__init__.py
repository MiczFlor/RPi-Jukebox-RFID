"""Compatibility plugin for configurations which still load ``playermpd``."""

import jukebox.plugs as plugs

from components.player import play_card_callbacks
from components.player.backends.mpd import MpdLock, PlayerMPD
from components.player.mpd_plugin import initialize_mpd_player


player_ctrl = None


@plugs.initialize
def initialize():
    global player_ctrl
    player_ctrl = initialize_mpd_player(__name__)


@plugs.atexit
def atexit(**ignored_kwargs):
    return player_ctrl.exit()


__all__ = ['MpdLock', 'PlayerMPD', 'play_card_callbacks']
