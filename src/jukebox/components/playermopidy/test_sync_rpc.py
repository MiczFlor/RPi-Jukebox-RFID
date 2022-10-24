from json import JSONDecoder
import string
import websocket
import threading
import logging
import json

#import functools
#import components.player
#import jukebox.cfghandler
#import jukebox.utils as utils
#import jukebox.plugs as plugs
#import jukebox.multitimer as multitimer
#import jukebox.publishing as publishing
#import jukebox.playlistgenerator as playlistgenerator
#import misc

#from jukebox.NvManager import nv_manager

from jsonrpcclient import Ok, parse_json, request_json
from websocket import create_connection


logger = logging.getLogger('jb.PlayerMopidy')

class PlayerMopidy:
    """Interface to Mopidy Daemon via RFC Json"""

    def __init__(self):
        #todo
        self.mopidy_url = "ws://192.168.178.42:6680/mopidy/ws" #cfg.getn('playermopidy', 'mopidy_url')
        self.mopidy_ws_client = None

        

    def exit(self):
        logger.debug("Exit routine of playermopidy started")
        self.status_is_closing = True
        self.status_thread.cancel()
        self.mopidy_ws_client.disconnect()
        #self.nvm.save_all()
        #return self.status_thread.timer_thread

    def connect(self):
        self.mopidy_ws_client = create_connection(self.mopidy_url)

    """def decode_2nd_swipe_option(self):
        #cfg_2nd_swipe_action = cfg.setndefault('playermpd', 'second_swipe_action', 'alias', value='none').lower()
        if cfg_2nd_swipe_action not in [*self.second_swipe_action_dict.keys(), 'none', 'custom']:
            logger.error(f"Config mpd.second_swipe_action must be one of "
                         f"{[*self.second_swipe_action_dict.keys(), 'none', 'custom']}. Ignore setting.")
        if cfg_2nd_swipe_action in self.second_swipe_action_dict.keys():
            self.second_swipe_action = self.second_swipe_action_dict[cfg_2nd_swipe_action]
        if cfg_2nd_swipe_action == 'custom':
            custom_action = utils.decode_rpc_call(cfg.getn('playermpd', 'second_swipe_action', default=None))
            self.second_swipe_action = functools.partial(plugs.call_ignore_errors,
                                                         custom_action['package'],
                                                         custom_action['plugin'],
                                                         custom_action['method'],
                                                         custom_action['args'],
                                                         custom_action['kwargs'])
"""
    def _send_get_json(self, method, parameters = None, data = None):
        """Schortcut for a fast message to mopidy through websocket"""
        req_json = self._build_rpc_message(method, parameters, data)
        self.mopidy_ws_client.send(req_json)
        response_json =  self.mopidy_ws_client.recv()
        return self._read_json_response(response_json)

    def _build_rpc_message(self, method, parameters = None, data = None):
        """Helper function to easily build the rpc json"""
        req_json = request_json(method,parameters)
        print("Request is:")
        print(req_json)
        return req_json
    
    def _read_json_response(self, response):
        print("Raw response is:")
        print(response) 

        try:
            response = parse_json(response) 
        except:
            response = json.loads(response) #events cannot be parsed by parse_json

        print("Json response is:")
        print(response)
        
        return response

    def _mpd_status_poll(self):
        """
        this method polls the status from mpd and stores the important inforamtion in the music_player_status,
        it will repeat itself in the intervall specified by self.mpd_status_poll_interval
        """
        """
        self.mpd_status.update(self.mpd_retry_with_mutex(self.mpd_client.status))
        self.mpd_status.update(self.mpd_retry_with_mutex(self.mpd_client.currentsong))

        if self.mpd_status.get('elapsed') is not None:
            self.current_folder_status["ELAPSED"] = self.mpd_status['elapsed']
            self.music_player_status['player_status']["CURRENTSONGPOS"] = self.mpd_status['song']
            self.music_player_status['player_status']["CURRENTFILENAME"] = self.mpd_status['file']

        if self.mpd_status.get('file') is not None:
            self.current_folder_status["CURRENTFILENAME"] = self.mpd_status['file']
            self.current_folder_status["CURRENTSONGPOS"] = self.mpd_status['song']
            self.current_folder_status["ELAPSED"] = self.mpd_status.get('elapsed', '0.0')
            self.current_folder_status["PLAYSTATUS"] = self.mpd_status['state']
            self.current_folder_status["RESUME"] = "OFF"
            self.current_folder_status["SHUFFLE"] = "OFF"
            self.current_folder_status["LOOP"] = "OFF"
            self.current_folder_status["SINGLE"] = "OFF"

        # Delete the volume key to avoid confusion
        # Volume is published via the 'volume' component!
        try:
            del self.mpd_status['volume']
        except KeyError:
            pass
        publishing.get_publisher().send('playerstatus', self.mpd_status)
        """

    #@plugs.tag
    def get_player_type_and_version(self):
        #with self.mpd_lock:
        #value = self.mopidy_ws_client.mpd_version()
        #return value
        pass

    #@plugs.tag
    def update(self):
        #with self.mpd_lock:
            #state = self.mpd_client.update()
        #return state
        pass

    #@plugs.tag
    def play(self):
        #with self.mpd_lock:
        return self._send_get_json("core.playback.play")

    #@plugs.tag
    def stop(self):
        #with self.mpd_lock:
            
        return self._send_get_json("core.playback.stop")

    #@plugs.tag
    def pause(self, state: int = 1):
        #TODO check card removal and re placement stuff
        """Enforce pause to state (1: pause, 0: resume)

        This is what you want as card removal action: pause the playback, so it can be resumed when card is placed
        on the reader again. What happens on re-placement depends on configured second swipe option
        """
        #with self.mpd_lock:
            #self.mpd_client.pause(state)
        state = self._send_get_json("core.playback.get_state")    
        if(state.result == "paused"):
            return self._send_get_json("core.playback.resume")
        
        return self._send_get_json("core.playback.pause")
    
    
    #@plugs.tag
    def prev(self):
        logger.debug("Prev")
        #with self.mpd_lock:
        return self._send_get_json("core.playback.previous")
        

    #@plugs.tag
    def next(self):
        """Play next track in current playlist"""
        logger.debug("Next")
        #with self.mpd_lock:
        return self._send_get_json("core.playback.next")

    #@plugs.tag
    def seek(self, new_time):
        with self.mpd_lock:
            self.mpd_client.seekcur(new_time)


    #@plugs.tag
    def shuffle(self):
        # As long as we don't work with waiting lists (aka playlist), this implementation is ok!
        shuffle_state = self._send_get_json("core.tracklist.get_random")    
        if(shuffle_state.result == True):
            return self._send_get_json("core.tracklist.set_random",{"value":False})
        
        return self._send_get_json("core.tracklist.set_random",{"value":True})

    #@plugs.tag
    def get_shuffle_state(self):
        # As long as we don't work with waiting lists (aka playlist), this implementation is ok!
        return self._send_get_json("core.tracklist.get_random") 
    
    #@plugs.tag
    def toggle(self):
        """Toggle pause state, i.e. do a pause / resume depending on current state"""
        logger.debug("Toggle")
        with self.mpd_lock:
            self.pause()
    
    """
    #@plugs.tag
    def rewind(self):
        ""
        Re-start current playlist from first track

        Note: Will not re-read folder config, but leave settings untouched""
        logger.debug("Rewind")
        with self.mpd_lock:
            self.mpd_client.play(1)

    #@plugs.tag
    def replay(self):
        ""
        Re-start playing the last-played folder

        Will reset settings to folder config""
        logger.debug("Replay")
        with self.mpd_lock:
            self.play_folder(self.music_player_status['player_status']['last_played_folder'])



    #@plugs.tag
    def replay_if_stopped(self):
        ""
        Re-start playing the last-played folder unless playlist is still playing

        .. note:: To me this seems much like the behaviour of play,
            but we keep it as it is specifically implemented in box 2.X""
        with self.mpd_lock:
            if self.mpd_status['state'] == 'stop':
                self.play_folder(self.music_player_status['player_status']['last_played_folder'])
"""
    #@plugs.tag
    def repeatmode(self, mode):
        if mode == 'repeat':
            repeat = True
            single = False
        elif mode == 'single':
            repeat = True
            single = True
        else:
            repeat = False
            single = False

        #with self.mpd_lock:
        self._send_get_json("core.tracklist.set_repeat",{"value":repeat})
        self._send_get_json("core.tracklist.set_single",{"value":single})

    #@plugs.tag
    def get_current_song(self, param):
        return self._send_get_json("core.playback.get_current_track")
    """
    #@plugs.tag
    def map_filename_to_playlist_pos(self, filename):
        # self.mpd_client.playlistfind()
        raise NotImplementedError

    #@plugs.tag
    def remove(self):
        raise NotImplementedError

    #@plugs.tag
    def move(self):
        # song_id = param.get("song_id")
        # step = param.get("step")
        # MPDClient.playlistmove(name, from, to)
        # MPDClient.swapid(song1, song2)
        raise NotImplementedError
    """
    #@plugs.tag
    def play_single(self, song_url):
        #with self.mpd_lock:
        #    self.mpd_client.clear()
        #    self.mpd_client.addid(song_url)
        #    self.mpd_client.play()
        self._send_get_json("core.tracklist.clear")
        self._send_get_json("core.tracklist.add",{'uris':{song_url}})
        self.play()

    """
    #@plugs.tag
    def resume(self):
        with self.mpd_lock:
            songpos = self.current_folder_status["CURRENTSONGPOS"]
            elapsed = self.current_folder_status["ELAPSED"]
            self.mpd_client.seek(songpos, elapsed)
            self.mpd_client.play()

    #@plugs.tag
    def play_card(self, folder: str, recursive: bool = False):
        ""
        Main entry point for trigger music playing from RFID reader. Decodes second swipe options before playing folder content

        Checks for second (or multiple) trigger of the same folder and calls first swipe / second swipe action
        accordingly.

        :param folder: Folder path relative to music library path
        :param recursive: Add folder recursively
        ""
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
        with self.mpd_lock:
            is_second_swipe = self.music_player_status['player_status']['last_played_folder'] == folder
        if self.second_swipe_action is not None and is_second_swipe:
            logger.debug('Calling second swipe action')
            self.second_swipe_action()
        else:
            logger.debug('Calling first swipe action')
            self.play_folder(folder, recursive)

    #@plugs.tag
    def get_folder_content(self, folder: str):
        ""
        Get the folder content as content list with meta-information. Depth is always 1.

        Call repeatedly to descend in hierarchy

        :param folder: Folder path relative to music library path
        ""
        plc = playlistgenerator.PlaylistCollector(components.player.get_music_library_path())
        plc.get_directory_content(folder)
        return plc.playlist

    #@plugs.tag
    def play_folder(self, folder: str, recursive: bool = False) -> None:
        ""
        Playback a music folder.

        Folder content is added to the playlist as described by :mod:`jukebox.playlistgenerator`.
        The playlist is cleared first.

        :param folder: Folder path relative to music library path
        :param recursive: Add folder recursively
        ""
        # TODO: This changes the current state -> Need to save last state
        with self.mpd_lock:
            logger.info(f"Play folder: '{folder}'")
            self.mpd_client.clear()

            plc = playlistgenerator.PlaylistCollector(components.player.get_music_library_path())
            plc.parse(folder, recursive)
            uri = '--unset--'
            try:
                for uri in plc:
                    self.mpd_client.addid(uri)
            except mpd.base.CommandError as e:
                logger.error(f"{e.__class__.__qualname__}: {e} at uri {uri}")
            except Exception as e:
                logger.error(f"{e.__class__.__qualname__}: {e} at uri {uri}")

            self.music_player_status['player_status']['last_played_folder'] = folder

            self.current_folder_status = self.music_player_status['audio_folder_status'].get(folder)
            if self.current_folder_status is None:
                self.current_folder_status = self.music_player_status['audio_folder_status'][folder] = {}

            self.mpd_client.play()
    """
    #@plugs.tag
    def play_album(self, album_url):
        """
        Playback a album from url
        TODO check whether url has album in it
        """
        #with self.mpd_lock:
        logger.info(f"Play album_url: '{album_url}")
        self._send_get_json("core.tracklist.clear")
        self._send_get_json("core.tracklist.add",{'uris':[album_url]})
        self.play()
    """
    #@plugs.tag
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

    #@plugs.tag
    def playerstatus(self):
        return self.mpd_status

    #@plugs.tag
    def playlistinfo(self):
        with self.mpd_lock:
            value = self.mpd_client.playlistinfo()
        return value

    # Attention: MPD.listal will consume a lot of memory with large libs.. should be refactored at some point
    #@plugs.tag
    def list_all_dirs(self):
        with self.mpd_lock:
            result = self.mpd_client.listall()
            # list = [entry for entry in list if 'directory' in entry]
        return result

    #@plugs.tag
    def list_albums(self):
        with self.mpd_lock:
            albums = self.mpd_retry_with_mutex(self.mpd_client.list, 'album', 'group', 'albumartist')

        return albums

    #@plugs.tag
    def list_song_by_artist_and_album(self, albumartist, album):
        with self.mpd_lock:
            albums = self.mpd_retry_with_mutex(self.mpd_client.find, 'albumartist', albumartist, 'album', album)

        return albums

    #@plugs.tag
    def get_song_by_url(self, song_url):
        with self.mpd_lock:
            song = self.mpd_retry_with_mutex(self.mpd_client.find, 'file', song_url)

        return song

    def get_volume(self):
        ""
        Get the current volume

        For volume control do not use directly, but use through the plugin 'volume',
        as the user may have configured a volume control manager other than MPD""
        #with self.mpd_lock:
        #   volume = self.mpd_client.status().get('volume')
        #return int(volume)

    def set_volume(self, volume):
        ""
        Set the volume

        For volume control do not use directly, but use through the plugin 'volume',
        as the user may have configured a volume control manager other than MPD""
        #with self.mpd_lock:
            #self.mpd_client.setvol(volume)
        #return self.get_volume()
"""


if __name__ == "__main__":
    """
    from websocket import create_connection

    ws = create_connection("ws://192.168.178.42:6680/mopidy/ws")
    print("Sending 'Hello, World'...")
    
    req = request_json("core.playback.stop")
    ws.send(req)
    print("Sent")
    print("Receiving...")
    result =  ws.recv()
    print("Received '%s'" % result)
    ws.close()
    """
    mopidy = PlayerMopidy();
    mopidy.connect()
    #mopidy.get_shuffle_state()
    #mopidy.shuffle()
    mopidy.play_album("tidal:album:121255042")
    mopidy.exit()
