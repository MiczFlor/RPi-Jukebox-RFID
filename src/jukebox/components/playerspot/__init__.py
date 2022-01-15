# -*- coding: utf-8 -*-
"""
Package for interfacing with the librespot-java API

Saving
{'player_status': {'last_played_folder': 'TraumfaengerStarkeLieder', 'CURRENTSONGPOS': '0',
                     'CURRENTFILENAME': 'TraumfaengerStarkeLieder/01.mp3'},
    'audio_folder_status':
       {'TraumfaengerStarkeLieder': {'ELAPSED': '1.0', 'CURRENTFILENAME': 'TraumfaengerStarkeLieder/01.mp3',
                                     'CURRENTSONGPOS': '0', 'PLAYSTATUS': 'stop', 'RESUME': 'OFF',
                                     'SHUFFLE': 'OFF', 'LOOP': 'OFF', 'SINGLE': 'OFF'},
        'Giraffenaffen': {'ELAPSED': '1.0', 'CURRENTFILENAME': 'TraumfaengerStarkeLieder/01.mp3',
                          'CURRENTSONGPOS': '0', 'PLAYSTATUS': 'play', 'RESUME': 'OFF', 'SHUFFLE': 'OFF',
                          'LOOP': 'OFF', 'SINGLE': 'OFF'}}}

References:
https://github.com/librespot-org/librespot-java
https://github.com/librespot-org/librespot-java/tree/dev/api
https://github.com/spocon/spocon
"""
import logging
import functools
import urllib.parse

import components.player
import jukebox.cfghandler
import jukebox.utils as utils
import jukebox.plugs as plugs
import jukebox.publishing as publishing
import misc

from .http_client import SpotifyHttpClient
from .ws_client import SpotifyWsClient

from jukebox.NvManager import nv_manager

logger = logging.getLogger('jb.PlayerSpot')
cfg = jukebox.cfghandler.get_handler('jukebox')


class PlayerSpot:
    """Interface to librespot-java API"""

    def __init__(self):
        self.nvm = nv_manager()
        host = cfg.getn('playerspot', 'host')
        http_client = SpotifyHttpClient(host)
        http_client.play_uri('spotify:track:3u0W3gJQNV5gegMmntzby8')

        # ws_client = SpotifyWsClient(host)
        # ws_client.connect()


    ###
    # TODO: The following functions have not been adopted to the new clients
    ###


    def exit(self):
        logger.debug("Exit routine of playerspot started")
        self.nvm.save_all()
        api_path = "/instance/close"
        requests_session.post(urllib.parse.urljoin(self.spot_api_baseurl, api_path))
        return "payerspot exited"

    def decode_2nd_swipe_option(self):
        cfg_2nd_swipe_action = cfg.setndefault('playerspot', 'second_swipe_action', 'alias', value='none').lower()
        if cfg_2nd_swipe_action not in [*self.second_swipe_action_dict.keys(), 'none', 'custom']:
            logger.error(f"Config spot.second_swipe_action must be one of "
                         f"{[*self.second_swipe_action_dict.keys(), 'none', 'custom']}. Ignore setting.")
        if cfg_2nd_swipe_action in self.second_swipe_action_dict.keys():
            self.second_swipe_action = self.second_swipe_action_dict[cfg_2nd_swipe_action]
        if cfg_2nd_swipe_action == 'custom':
            custom_action = utils.decode_rpc_call(cfg.getn('playerspot', 'second_swipe_action', default=None))
            self.second_swipe_action = functools.partial(plugs.call_ignore_errors,
                                                         custom_action['package'],
                                                         custom_action['plugin'],
                                                         custom_action['method'],
                                                         custom_action['args'],
                                                         custom_action['kwargs'])

    def _spot_status_poll(self):
        """
        this method polls the status from spot and stores the important inforamtion in the music_player_status,
        it will repeat itself in the intervall specified by self.spot_status_poll_interval
        """

        # Delete the volume key to avoid confusion
        # Volume is published via the 'volume' component!
        try:
            del self.spot_status['volume']
        except KeyError:
            pass
        publishing.get_publisher().send('playerstatus', self.spot_status)

    @staticmethod
    def _handle_http_errors(requests_response: requests.Response):
        try:
            requests_response.raise_for_status()
        except requests.HTTPError as http_error:
            logger.error("Could not communicate with spotify API")
            logger.error(f"Reason: {http_error}")
            return False
        except Exception as err:
            logger.error(f"Other error occurred: {err}")
            return False
        return True

    @plugs.tag
    def load(self, uri: str, start_playing: bool):
        logger.debug(f"loading playlist {uri} and with option playing={start_playing}")
        self.check_uri(uri)
        api_path = f"/player/load?uri={uri}&play={start_playing}"
        spot_response = requests_session.post(urllib.parse.urljoin(self.spot_api_baseurl, api_path))
        self._handle_http_errors(spot_response)

    @plugs.tag
    def play(self):
        api_path = "/player/resume"
        spot_response = requests_session.post(urllib.parse.urljoin(self.spot_api_baseurl, api_path))
        self._handle_http_errors(spot_response)

    @plugs.tag
    def stop(self):
        self.pause(state=1)

    @plugs.tag
    def pause(self, state: int = 1):
        """Enforce pause to state (1: pause, 0: resume)

        This is what you want as card removal action: pause the playback, so it can be resumed when card is placed
        on the reader again. What happens on re-placement depends on configured second swipe option
        """
        if state == 1:
            api_path = "/player/pause"
            spot_response = requests_session.post(urllib.parse.urljoin(self.spot_api_baseurl, api_path))
            self._handle_http_errors(spot_response)
        else:
            self.play()

    @plugs.tag
    def prev(self):
        api_path = "/player/prev"

        spot_response = requests_session.post(urllib.parse.urljoin(self.spot_api_baseurl, api_path))
        self._handle_http_errors(spot_response)

    @plugs.tag
    def next(self):
        api_path = "/player/next"
        spot_response = requests_session.post(urllib.parse.urljoin(self.spot_api_baseurl, api_path))
        self._handle_http_errors(spot_response)

    @plugs.tag
    def seek(self, new_time: int):
        """
        Seek to a given position in milliseconds specified by new_time
        """
        api_path = f"/player/seek?position_ms={new_time}"
        spot_response = requests_session.post(urllib.parse.urljoin(self.spot_api_baseurl, api_path))
        self._handle_http_errors(spot_response)

    @plugs.tag
    def shuffle(self, random: bool):
        api_path = f"/player/shuffle?state={1 if random else 0}"
        spot_response = requests_session.post(urllib.parse.urljoin(self.spot_api_baseurl, api_path))
        self._handle_http_errors(spot_response)

    @plugs.tag
    def rewind(self):
        """
        Re-start current playlist from first track

        Note: Will not re-read folder config, but leave settings untouched"""
        logger.debug("Rewind")
        self.seek(0)

    @plugs.tag
    def replay(self):
        """
        Re-start playing the last-played playlist

        Will reset settings to folder config"""
        logger.debug("Replay")
        self.play_playlist(self.music_player_status['player_status']['last_played_folder'])

    @plugs.tag
    def toggle(self):
        """Toggle pause state, i.e. do a pause / resume depending on current state"""
        logger.debug("Toggle")
        api_path = "/player/play-pause"
        spot_response = requests_session.post(urllib.parse.urljoin(self.spot_api_baseurl, api_path))
        self._handle_http_errors(spot_response)

    @plugs.tag
    def replay_if_stopped(self):
        """
        Re-start playing the last-played folder unless playlist is still playing

        .. note:: To me this seems much like the behaviour of play,
            but we keep it as it is specifically implemented in box 2.X"""
        logger.debug("replay_if_stopped")
        if self.spot_status['state'] == 'stop':
            self.play_playlist(self.music_player_status['player_status']['last_played_folder'])

    @plugs.tag
    def repeatmode(self, mode: str):
        if mode == 'repeat':
            rep_state = "context"
        elif mode == 'single':
            rep_state = "track"
        else:
            rep_state = "none"
        api_path = f"/player/repeat?state={rep_state}"
        spot_response = requests_session.post(urllib.parse.urljoin(self.spot_api_baseurl, api_path))
        self._handle_http_errors(spot_response)

    @plugs.tag
    def get_current_song(self, param):
        return self.spot_status

    @plugs.tag
    def map_filename_to_playlist_pos(self, filename):
        raise NotImplementedError

    @plugs.tag
    def remove(self):
        raise NotImplementedError

    @plugs.tag
    def move(self):
        raise NotImplementedError

    @plugs.tag
    def play_single(self, song_uri: str):
        self.check_uri(song_uri)
        api_path = f"/player/repeat?uri={song_uri}&play=true"
        spot_response = requests_session.post(urllib.parse.urljoin(self.spot_api_baseurl, api_path))
        self._handle_http_errors(spot_response)

    @plugs.tag
    def resume(self):
        songpos = self.current_folder_status["CURRENTSONGPOS"]
        self.seek(songpos)
        self.play()

    @plugs.tag
    def play_card(self, folder: str, recursive: bool = False):
        """
        Main entry point for trigger music playing from RFID reader. Decodes second swipe options before
        playing folder content

        Checks for second (or multiple) trigger of the same folder and calls first swipe / second swipe action
        accordingly.

        :param folder: Folder path relative to music library path
        :param recursive: Add folder recursively
        """
        # Developers notes:
        #
        #     * 2nd swipe trigger may also happen, if playlist has already stopped playing
        #       --> Generally, treat as first swipe
        #     * 2nd swipe of same Card ID may also happen if a different song has been played in between from WebUI
        #       --> Treat as first swipe
        #     * With place-not-swipe: Card is placed on reader until playlist expieres. Music stop. Card is removed and
        #       placed again on the reader: Should be like first swipe
        #     * TODO: last_played_folder is restored after box start, so first swipe of last played card may look like
        #       second swipe
        #
        logger.debug(f"last_played_folder = {self.music_player_status['player_status']['last_played_folder']}")
        logger.debug(f"last_played_folder = {self.music_player_status['player_status']['last_played_folder']}")
        is_second_swipe = self.music_player_status['player_status']['last_played_folder'] == folder
        if self.second_swipe_action is not None and is_second_swipe:
            logger.debug('Calling second swipe action')
            self.second_swipe_action()
        else:
            logger.debug('Calling first swipe action')
            self.play_playlist(folder, recursive)

    @plugs.tag
    def get_playlist_content(self, playlist_uri: str):
        """
        Get the spotify playlist as content list with spotify id

        Example:
        ["artists" : [{
           "id" : "5lpH0xAS4fVfLkACg9DAuM",
           "name" : "Wham!"
         }],
         "id" : "2FRnf9qhLbvw8fu4IBXx78",
         "name" : "Last Christmas"
         }]


        :param playlist_uri: URI for the spotify playlist as string
        """
        track_list = []
        api_path = f"/web-api/v1/playlists/{playlist_uri}/tracks?fields=items(track(name,id,artists(name,id))"
        playlist_response = requests_session.post(urllib.parse.urljoin(self.spot_api_baseurl, api_path))
        if self._handle_http_errors(playlist_response):
            playlist_dict = playlist_response.json()
            for elem in playlist_dict["items"]:
                track_list.append(elem["track"])
        return track_list

    @plugs.tag
    def play_playlist(self, playlist_uri: str, recursive: bool = False) -> None:
        """
        Playback a spotify playlist.

        :param playlist_uri: Folder path relative to music library path
        :param recursive: Add folder recursively
        """
        logger.debug("play_folder")
        logger.info(f"Play spotify playlist: '{playlist_uri}'")

        self.music_player_status['player_status']['last_played_folder'] = playlist_uri

        self.current_folder_status = self.music_player_status['audio_folder_status'].get(playlist_uri)
        if self.current_folder_status is None:
            self.current_folder_status = self.music_player_status['audio_folder_status'][playlist_uri] = {}

        self.load(self.current_folder_status, start_playing=True)

    @plugs.tag
    def play_album(self, album_uri: str):
        """
        Playback a album from spotify.

        :param album_uri: Album URI from spotify
        """
        logger.debug("play_album")
        logger.info(f"Play album: '{album_uri}'")
        self.load(album_uri, start_playing=True)

    @plugs.tag
    def queue_load(self, folder):
        # There was something playing before -> stop and save state
        # Clear the queue
        # Check / Create the playlist
        #  - not needed if same folder is played again? Buf what if files have been added a mpc update has been run?
        #  - and this a re-trigger to start the new playlist
        # If we must update the playlists everytime anyway why write them to file and not just keep them in the queue?
        # Load the playlist
        # Get folder config and apply settings
        pass

    @plugs.tag
    def playerstatus(self):
        return self.spot_status

    @plugs.tag
    def playlistinfo(self):
        """
        Returns a list of all songs in the playlist
        """
        track_list = []
        playlist_uri = self.get_playback_state()["context"]["uri"]
        api_path = f"/web-api/v1/playlists/{playlist_uri}/tracks?fields=items(track(name))"
        playlist_response = requests_session.post(urllib.parse.urljoin(self.spot_api_baseurl, api_path))
        if self._handle_http_errors(playlist_response):
            playlist_response.raise_for_status()
            playlist_dict = playlist_response.json()
            for elem in playlist_dict["items"]:
                track_list.append(elem["track"]["name"])
        return track_list

    @plugs.tag
    def list_albums(self):
        # ToDo: Do we need this for spotify?
        raise NotImplementedError

    @plugs.tag
    def list_song_by_artist_and_album(self, albumartist, album):
        # ToDo: Do we need this for spotify?
        raise NotImplementedError

    def get_volume(self):
        """
        Get the current volume

        For volume control do not use directly, but use through the plugin 'volume',
        as the user may have configured a volume control manager other than Spotify"""
        return self.get_playback_state()["device"]["volume_percent"]

    def set_volume(self, volume):
        """
        Set the volume

        For volume control do not use directly, but use through the plugin 'volume',
        as the user may have configured a volume control manager other than Spotify"""
        api_path = f"/player/volume?volume_percent={volume}"
        spot_response = requests_session.post(urllib.parse.urljoin(self.spot_api_baseurl, api_path))
        self._handle_http_errors(spot_response)
        return self.get_volume()

    def get_playback_state(self):
        playback_state_dict = {}
        api_path = "/web-api/v1/me/player"
        playback_state = requests_session.post(urllib.parse.urljoin(self.spot_api_baseurl, api_path))
        if self._handle_http_errors(playback_state):
            playback_state_dict = playback_state.json()
        return playback_state_dict if playback_state_dict["device"]["id"] == self.device_info["device_id"] else {}

    @staticmethod
    def check_uri(uri: str):
        """
        Checking that the uri has the right syntax
        """
        check_list = uri.split(":")
        valid_play_type = ["album", "track"]
        if check_list[1] == "user":
            assert len(check_list) == 5, f"URI {uri} is missing information."
            assert check_list[0] == "spotify", f"URI {uri} does not start with spotify"
            assert check_list[1] == "user", f"URI {uri} does not contain a valid type on pos 2"
            assert type(check_list[2]) is int, f"URI {uri} does not contain the right user id on pos 3"
            assert check_list[3] == "playlist", f"URI {uri} does not contain a valid type playlist on pos 4"

        else:
            assert len(check_list) == 3, f"URI {uri} is missing information."
            assert check_list[0] == "spotify", f"URI {uri} does not start with spotify"
            assert check_list[1] in valid_play_type, f"URI {uri} does not contain a valid type on pos 2"


# ---------------------------------------------------------------------------
# Plugin Initializer / Finalizer
# ---------------------------------------------------------------------------

player_ctrl: PlayerSpot


@plugs.initialize
def initialize():
    global player_ctrl
    player_ctrl = PlayerSpot()
    plugs.register(player_ctrl, name='ctrl')

    # Check user rights on music library
    library_check_user_rights = cfg.setndefault('playerspot', 'library', 'check_user_rights', value=True)
    if library_check_user_rights is True:
        music_library_path = components.player.get_music_library_path()
        if music_library_path is not None:
            logger.info(f"Change user rights for {music_library_path}")
            misc.recursive_chmod(music_library_path, mode_files=0o666, mode_dirs=0o777)


@plugs.atexit
def atexit(**ignored_kwargs):
    global player_ctrl
    return player_ctrl.exit()
