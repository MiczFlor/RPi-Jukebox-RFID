# Copyright: 2022
# SPDX License Identifier: MIT License

import logging
import os.path
import os

from ruamel import yaml
from spotipy import CacheFileHandler

import jukebox.plugs as plugin
import jukebox.cfghandler

from spotipy.oauth2 import SpotifyOAuth
import spotipy

logger = logging.getLogger('jb.spotify')
cfg = jukebox.cfghandler.get_handler('jukebox')


def sanitize(path: str):
    return os.path.normpath(path).lstrip('./')


class SPOTBackend:
    def __init__(self, player_status):
        host = cfg.getn('playerspot', 'host')
        self.player_status = player_status
        self.cache_handler = CacheFileHandler(cache_path='../../shared/spotify/')
        self.cache_file = '../../shared/spotify/.spotipyoauthcache'
        self.client_id = cfg.setndefault('playerspot', 'client_id', value='Phoniebox')
        self.client_secret = cfg.setndefault('playerspot', 'client_secret', value='Phoniebox_secret')
        self.redirect_uri = cfg.setndefault('playerspot', 'callback_url',
                                            value='http://localhost:3001')

        spot_scope = "user-read-playback-state,user-modify-playback-state"
        try:
            self.auth_manager = SpotifyOAuth(open_browser=False, scope=spot_scope, client_id=self.client_id, client_secret=self.client_id, redirect_uri=self.redirect_uri, cache_path=sanitize(self.cache_file))
            self.auth_uri = self.auth_manager.get_authorize_url()
            logger.info(f"Please log in here: {self.auth_uri}")
        except Exception as err:
            logger.error(err)

        #self.collection_file_location = cfg.setndefault('playerspot', 'collection_file',
        #                                                value="../../shared/audio/spotify/spotify_collection.yaml")
        #self.spotify_collection_data = self._read_data_file()

    @plugin.tag
    def init_spotclient(self, spot_code=None):
        token_info = self.auth_manager.get_cached_token()
        logger.debug(f"Token Info: {token_info}")

        if token_info:
            logger.debug("Found cached token for Spotify Client!")
            access_token = token_info['access_token']
        else:
            # ToDo: implement this within the web app
            token_info = self.auth_manager.get_access_token(spot_code)
            access_token = token_info['access_token']

        if access_token:
            self.spot_client = spotipy.Spotify(access_token)
            self.auth_code = cfg.setndefault('playerspot', 'auth_code', value=access_token)

    def _read_data_file(self) -> dict:
        try:
            with open(self.collection_file_location, "r") as collection_file:
                return yaml.safe_load(collection_file.read())
        except Exception as err:
            logger.error(f"Could not open spotify collection file {self.collection_file_location}")
            logger.debug(f"Error: {err}")
            logger.debug("Continuing with empty dictionary")
            return {}

    def play(self):
        return self.spot_client.start_playback()

    def pause(self):
        return self.spot_client.pause_playback()

    def stop(self):
        return self.spot_client.pause_playback()

    def prev(self):
        return self.spot_client.previous_track()

    def next(self):
        return self.spot_client.next_track()

    def toggle(self):
        pass

    def get_queue(self):
        pass

    @plugin.tag
    def play_uri(self, uri: str, **kwargs):
        """Decode URI and forward play call

        spotify:playlist:0
            --> search in the yaml-file for the type "playlist" and play the first uri
        """
        player_type, index = uri.split(':', 1)
        if player_type != 'spotify':
            raise KeyError(f"URI prefix must be 'spotify' not '{player_type}")

        return self.spot_client.start_playback(context_uri=uri)

    @plugin.tag
    def get_status(self):
        return self.spot_client.current_user()

    # -----------------------------------------------------
    # Queue / URI state  (save + restore e.g. random, resume, ...)

    def save_state(self):
        """Save the configuration and state of the current URI playback to the URIs state file"""
        pass

    def _restore_state(self):
        """
        Restore the configuration state and last played status for current active URI
        """
        pass
