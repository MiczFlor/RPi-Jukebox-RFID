# Copyright: 2022
# SPDX License Identifier: MIT License

import logging
import os.path

from ruamel import yaml

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
        self.client_id = cfg.setndefault('playerspot', 'client_id', value='Phoniebox')
        self.client_secret = cfg.setndefault('playerspot', 'client_secret', value='Phoniebox_secret')
        self.redirect_uri = cfg.setndefault('playerspot', 'callback_url',
                                                         value='https://localhost:8888/callback')
        self.auth_manager = SpotifyOAuth(scope="streaming", client_id=self.client_id, client_secret=self.client_id, redirect_uri=self.redirect_uri)

        self.spot_client = spotipy.Spotify(auth_manager=self.auth_manager)

        #self.collection_file_location = cfg.setndefault('playerspot', 'collection_file',
        #                                                value="../../shared/audio/spotify/spotify_collection.yaml")
        #self.spotify_collection_data = self._read_data_file()

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
        self.spot_client.start_playback(self.client_id)

    def pause(self):
        self.spot_client.pause_playback(self.client_id)

    def stop(self):
        self.spot_client.pause_playback(self.client_id)

    def prev(self):
        self.spot_client.previous_track(self.client_id)

    def next(self):
        self.spot_client.next_track()
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

        self.spot_client.start_playback(self.client_id, uri)

    @plugin.tag
    def get_status(self):
        logger.debug(self.spot_client.current_playback())
        self.spot_client.current_playback()

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
