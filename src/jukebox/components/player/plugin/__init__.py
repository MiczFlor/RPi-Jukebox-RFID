# Copyright: 2022
# SPDX License Identifier: MIT License

import asyncio
import logging
import threading
from typing import Optional

import jukebox.plugs as plugin
import jukebox.cfghandler
from components.player.backends.mpd.interfacing_mpd import MPDBackend
from components.player.backends.spotify.interfacing_spotify import SPOTBackend
from components.player.core import PlayerCtrl
from components.player.core.player_status import PlayerStatus

from components.player.core.player_content import PlayerData


logger = logging.getLogger('jb.player')
cfg = jukebox.cfghandler.get_handler('jukebox')

# Background event loop in a separate thread to be used by backends as needed for asyncio tasks
event_loop: asyncio.AbstractEventLoop

# The top-level player arbiter that acts as the single interface to the outside
player_arbiter: PlayerCtrl

# Player status needed for webapp
player_status: PlayerStatus

# The various backends
backend_mpd: Optional[MPDBackend] = None
backend_spot: Optional[SPOTBackend] = None


def start_event_loop(loop: asyncio.AbstractEventLoop):
    # https://docs.python.org/3/library/asyncio-eventloop.html#asyncio.loop.shutdown_asyncgens
    logger.debug("Start player AsyncIO Background Event Loop")
    try:
        loop.run_forever()
    finally:
        loop.run_until_complete(loop.shutdown_asyncgens())
        loop.close()


def register_mpd():
    global event_loop
    global backend_mpd
    global player_arbiter

    backend_mpd = MPDBackend(event_loop)
    # Register with plugin interface to call directly
    plugin.register(backend_mpd, package='player', name='mpd')
    player_arbiter.register('mpd', backend_mpd)


def register_spotify():
    global event_loop
    global backend_spot
    global player_arbiter
    global player_status

    backend_spot = SPOTBackend(player_status, event_loop)
    # Register with plugin interface to call directly
    plugin.register(backend_spot, package='player', name='spotify')
    player_arbiter.register('spotify', backend_spot)


@plugin.initialize
def initialize():
    global event_loop
    global player_arbiter
    global player_status
    # Create the event loop and start it in a background task
    # the event loop can be shared across different backends (if the backends require a async event loop)
    event_loop = asyncio.new_event_loop()
    t = threading.Thread(target=start_event_loop, args=(event_loop,), daemon=True, name='PlayerEventLoop')
    t.start()

    player_arbiter = PlayerCtrl()

    player_status = PlayerStatus()
    player_status.publish()

    player_content = PlayerData()

    # Create and register the players (this is explicit for the moment)
    register_spotify()
    register_mpd()

    plugin.register(player_arbiter, package='player', name='ctrl')
    plugin.register(player_content, package='player', name='content')


@plugin.atexit
def atexit(**ignored_kwargs):
    global event_loop
    event_loop.stop()
