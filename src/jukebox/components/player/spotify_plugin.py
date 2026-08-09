"""Spotify backend composition and shared service registration."""

import logging

import jukebox.cfghandler

from .backends.spotify import SpotifyPlayer
from .spotify import create_spotify_service


logger = logging.getLogger('jb.player.spotify')
cfg = jukebox.cfghandler.get_handler('jukebox')
_spotify_service = None


def configure_spotify(player_ctrl):
    """Create Spotify services and register playback when explicitly enabled."""
    global _spotify_service

    enabled = cfg.setndefault('players', 'spotify', 'enabled', value=False)
    client_id = cfg.setndefault('players', 'spotify', 'client_id', value='')
    redirect_uri = cfg.setndefault('players', 'spotify', 'redirect_uri', value='')
    token_file = cfg.setndefault(
        'players',
        'spotify',
        'token_file',
        value='../../shared/settings/spotify_tokens.json',
    )
    library_file = cfg.setndefault(
        'players',
        'spotify',
        'library_file',
        value='../../shared/settings/spotify_library.json',
    )
    device_name = cfg.setndefault(
        'players',
        'spotify',
        'device_name',
        value='Phoniebox',
    )
    _spotify_service = create_spotify_service(
        client_id,
        redirect_uri,
        token_file,
        device_name,
        library_file,
    )
    _spotify_service.enabled = bool(enabled)

    if enabled:
        player_ctrl.register_backend('spotify', SpotifyPlayer(_spotify_service))
        logger.info("Enabled Spotify player backend for device '%s'", device_name)
    return _spotify_service


def get_spotify_service():
    return _spotify_service
