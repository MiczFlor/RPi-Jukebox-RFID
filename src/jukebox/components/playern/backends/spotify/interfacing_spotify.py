# Copyright: 2022
# SPDX License Identifier: MIT License

import logging
import os.path

from ruamel import yaml

import jukebox.plugs as plugin
import jukebox.cfghandler
from components.playern.backends.spotify.http_client import SpotifyHttpClient
from components.playern.backends.spotify.ws_client import SpotifyWsClient

logger = logging.getLogger('jb.spotify')
cfg = jukebox.cfghandler.get_handler('jukebox')


def sanitize(path: str):
    return os.path.normpath(path).lstrip('./')


class SPOTBackend:
    def __init__(self, player_status):
        host = cfg.getn('playerspot', 'host')
        self.player_status = player_status

        self.http_client = SpotifyHttpClient(host)

        self.ws_client = SpotifyWsClient(
            host=host,
            player_status=self.player_status
        )
        self.ws_client.connect()

        self.collection_file_location = cfg.setndefault('playerspot', 'collection_file',
                                                   value="../../shared/audio/spotify/spotify_collection.yaml")
        self.spotify_collection_data = self._read_data_file()

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
        self.http_client.play()

    def pause(self):
        self.http_client.pause()

    def prev(self):
        self.http_client.prev()

    def next(self):
        self.http_client.next()

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
        player_type, list_type, index = uri.split(':', 2)
        if player_type != 'spotify':
            raise KeyError(f"URI prefix must be 'spotify' not '{player_type}")

        self.http_client.play_uri(self.spotify_collection_data.get(list_type)[int(index)].get("uri"))

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
