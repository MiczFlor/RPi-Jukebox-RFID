"""
Backend:
    An interface to an player we use for playback, i.e. MDP or Spotify

Flavor:
    An abstraction layer between backend and API, to enable different types of playback contents with the same backend
    With MPD, we can playback by album or disk folder.
    We also use MPD to play back Podcasts (with a custom decoder int the middle)
    This all needs different ways of retrieving and storing playlists, status, etc
    But, we still want to use the same MPD instance

PlayerCtrl:
    Top-level player which abstracts the various flavors and backends. All play, stop etc commands controlling
    current playback go through this instance. This is mandatory, as we may need to switch between player backends from
    one playback to another

Playlist:
    Any kind of concatenated set of songs that somehow belong together and are indexed by a URI.
    E.g.the content folder, the songs of an album, the music files of a podcast

URI:
    The link to a playlist. I.e. the path to a directory, the album_artist & album to identify the album
    the path to a podcast link file, spotify uri file, ...

Queue:
    The currently active playlist as loaded in the backend

How it works:

The backends register the flavor(s) with the top-level player control. The WebApp goes through player.play(flavor, uri)
to trigger a playback. Function like next, prev also go through the player control - here the currently active flavor is
automatically selected by the player control.

To get all playlists and/or playlist entries, the WebApp also goes through the player control - it is the same function
but takes different arguments depending on player control. And returns different results (possibly in different formats?)

Displaying what can be played back:

get_list: List all possible playlists (can be playlists only for a URI prefix - e.g. a folder)

get_content: List all songs in a playlist

Examples:
    player.play(flavor=folder, uri='conni_backt')
    > plays folder content of audiopath/conni_backt/*

    player.play(flavor=spotify, uri=lausemaus/leo_will_nicht_teilen.spotify')
    > plays a spotify playlist for which the Spotify URI is in file lausemaus/leo_will_nicht_teilen.spotify

    player.play(flavor=album, album_artist=benjamin, album=ImZirkus)
    > plays form MPD database the songs from the album that matches album_artist=benjamin, album=ImZirkus)

    player.get_list(flavor=folder, uri='.')
    > [conni_backt, connie_zeltet]

    player.get_content(flavor=folder, uri='connie_backt')
    > [01-song.mp3, 02-intro, ...]

    NOTE: list and get_content return not only names of files, but list of tuples which also contain path and
    filetype (dir, file)

    ...

"""

from typing import Dict, Callable, Optional


class PlayerFlavorEntry:
    def __init__(self, flavor_name: str,
                 backend,
                 play_callable: Callable,
                 get_list_callable: Callable,
                 get_content_callable: Callable):
        self._backend = backend
        self._flavor_name = flavor_name
        self._play = play_callable
        self._list = get_list_callable
        self._content = get_content_callable

    @property
    def play(self):
        return self._play

    @property
    def get_list(self):
        return self._list

    @property
    def get_content(self):
        return self._content

    def __getattr__(self, attr):
        """Forward all not specially mapped function calls to the actual backend"""
        return getattr(self.backend, attr)


class PlayerCtrl:
    """The top-level player instance through which all calls go. Arbitrates between the different backends"""

    def __init__(self):
        self._flavors: Dict[str, PlayerFlavorEntry] = {}
        self._active: Optional[PlayerFlavorEntry] = None

    def register(self, flavor: str, backend,
                 play_callable: Callable,
                 get_list_callable: Callable,
                 get_content_callable: Callable):
        self._flavors[flavor] = PlayerFlavorEntry(flavor, backend, play_callable, get_list_callable,
                                                  get_content_callable)

    def play(self, flavor, check_second_swipe=False, **kwargs):
        # Save the current state (if something is playing)
        # Stop the current playback
        # Decode card second swipe
        # And finally play
        self._active = self._flavors[flavor]
        self._active.play(**kwargs)

    def stop(self):
        # Save current state for resume functionality
        self._save_state()

        self._active.stop()

    def next(self):
        self._active.next()

    def get_queue(self):
        self._active.get_queue()

    def _save_state(self):
        # Get the backend to save the state of the current playlist to the URI's config file
        self._active.save_queue_state_to_uri()
        # Also need to save which backend and URI was currently playing to be able to restore it after reboot
        pass


class BackendMPD:
    """Example Backend for MPD - do the same for other backends"""

    # def play(self, uri):
    #     # Get URI state
    #     get_uri_state()
    #     # Apply last state
    #     # play

    # ----------------------------------
    # Stuff that replaces the current playlist and starts a new playback for URI
    #

    def play_folder(self, uri, recursive=False):
        pass

    def play_single(self, uri):
        pass

    def play_album(self, album_artist: str, album: str):
        pass

    def play_podcast(self, uri):
        pass

    # ----------------------------------
    # Get lists of playlists (one for each flavor)

    def get_folder_list(self, uri):
        """List folder contents (files and directories)"""
        pass

    def get_album_list(self):
        """Returns all albums in database"""
        pass

    def get_podcast_list(self, uri):
        """List all podcasts in directory :attr:`uri`"""
        pass

    # ----------------------------------
    # Get all songs of a playlists (one function for each flavor)

    def get_folder_content(self, uri):
        """Just to unify the API for all flavors"""
        return self.get_folder_list(uri)

    def get_album_content(self, album_artist, album):
        """Returns all song of an album"""
        pass

    def get_podcast_content(self, uri):
        """Lists playlist of one podcast file"""
        pass

    # ----------------------------------
    # Stuff that controls current playback (i.e. moves around in the current playlist, termed "the queue")

    def next(self):
        pass

    def seek(self, time):
        """Seek to position :attr:`time` in current song"""
        pass

    def jump(self, position):
        """Jump to song at position is in the active playback queue"""
        # Play song (id, uri, ##?) that is in current playlist
        # but without changing the current playlist (i.e. like going next, next, next instead of play_single(URI)
        pass

    # ----------------------------------
    # Stuff that modifies the queue or informs about it
    # We do not allow modifying the queue at the moment

    def get_queue(self):
        """Displays a list of all songs in the currently active playlist"""
        pass

    # ----------------------------------
    # Modifying playback behaviour

    def set_queue_config(self, resume=None, random=None, single=None, loop=None):
        """Sets the config for the currently active playback

        These settings will also be saved automatically to URI config!"""
        pass

    def save_queue_state_to_uri(self):
        """Save the current queue state (resume, random, ...) and current song position to the URI the queue was loaded from"""
        # Get state (resume, ..., elapsed, current song)
        # Save to database
        pass

    # ----------------------------------
    # Modifying playlist's config independent of the current queue

    def set_playlist_config(self, uri, resume=None, random=None, single=None, loop=None):
        """Change the config for a specific playlist w/o touching current playback"""
        pass


def initialize():
    player = PlayerCtrl()
    mpd = BackendMPD()
    player.register('album',
                    mpd,
                    lambda album_artist, album, **ignored_kwargs: mpd.play_album(album_artist=album_artist,
                                                                                 album=album),
                    lambda **ignored_kwargs: mpd.get_album_list(),
                    lambda album_artist, album, **ignored_kwargs: mpd.get_album_content(album_artist=album_artist,
                                                                                        album=album))
    player.register('folder',
                    mpd,
                    lambda uri, recursive=False, **ignore_kwargs: mpd.play_folder(uri=uri, recursive=recursive),
                    lambda uri, **ignore_kwargs: mpd.get_folder_list(uri=uri),
                    lambda uri, **ignore_kwargs: mpd.get_folder_content(uri=uri))
