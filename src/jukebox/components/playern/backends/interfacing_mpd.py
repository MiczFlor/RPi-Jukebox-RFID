# Copyright: 2022
# SPDX License Identifier: MIT License

import asyncio
import logging
import os.path
import re

import jukebox.plugs as plugin
import jukebox.cfghandler

from mpd.asyncio import MPDClient

logger = logging.getLogger('jb.mpd')
cfg = jukebox.cfghandler.get_handler('jukebox')


def sanitize(path: str):
    return os.path.normpath(path).lstrip('./')


class MPDBackend:

    def __init__(self, event_loop):
        self.client = MPDClient()
        self.loop = event_loop
        self.host = cfg.getn('players', 'mpd', 'host', default='localhost')
        self.port = '6600'
        self._flavors = {'folder': self.get_files,
                         'file': self.get_track,
                         'album': self.get_album_from_uri,
                         'podcast': self.get_podcast,
                         'livestream': self.get_livestream}
        self._active_uri = ''
        # TODO: If connect fails on first try this is non recoverable
        self.connect()
        # Start the status listener in an endless loop in the event loop
        asyncio.run_coroutine_threadsafe(self._status_listener(), self.loop)

    # ------------------------------------------------------------------------------------------------------
    # Bring calls to client functions from the synchronous part into the async domain
    # Async function of the MPD client return a asyncio.future as a result
    # That means we must
    #  - first await the function execution in the event loop
    #     _run_cmd_async: an async function
    #  - second then wait for the future result to be available in the sync domain
    #     _run_cmd: a sync function that schedules the async function in the event loop for execution
    #               and wait for the future result by calling ..., self.loop).result()
    # Since this must be done for every command crossing the async/sync domain, we keep it generic and
    # pass method and arguments to these two wrapper functions that do the scheduling and waiting

    async def _run_cmd_async(self, afunc, *args, **kwargs):
        return await afunc(*args, **kwargs)

    def _run_cmd(self, afunc, *args, **kwargs):
        return asyncio.run_coroutine_threadsafe(self._run_cmd_async(afunc, *args, **kwargs), self.loop).result()

    # -----------------------------------------------------
    # Check and update statues

    async def _connect(self):
        return await self.client.connect(self.host, self.port)

    def connect(self):
        # May raise: mpd.base.ConnectionError: Can not send command to disconnected client
        result = asyncio.run_coroutine_threadsafe(self._connect(), self.loop).result()
        logger.debug(f"Connected to MPD version {self.client.mpd_version} @ {self.host}:{self.port}")
        return result

    # -----------------------------------------------------
    # Check and update statues

    async def _status_listener(self):
        """The endless status listener: updates the status whenever there is a change in one MPD subsystem"""
        # Calls to logger do not work
        # logger.debug("MPD Status Listener started")
        async for subsystem in self.client.idle():
            # logger.debug("MPD: Idle change in", subsystem)
            s = await self.client.status()
            # logger.debug(f"MPD: New Status: {s.result()}")
            print(f"MPD: New Status: {type(s)} // {s}")
            # Now, do something with it ...

    async def _status(self):
        return await self.client.status()

    @plugin.tag
    def status(self):
        """Refresh the current MPD status (by a manual, sync trigger)"""
        f = asyncio.run_coroutine_threadsafe(self._status(), self.loop).result()
        print(f"Status: {f}")
        # Put it into unified structure and notify global player control

    # -----------------------------------------------------
    # Stuff that controls current playback (i.e. moves around in the current playlist, termed "the queue")

    def next(self):
        return self._run_cmd(self.client.next)

    def prev(self):
        return self._run_cmd(self.client.prev)

    @plugin.tag
    def play(self, idx=None):
        """
        If idx /= None, start playing song idx from queue
        If stopped, start with first song in queue
        If paused, resume playback at current position
        """
        # self.client.play() continues playing at current position
        if idx is None:
            return self._run_cmd(self.client.play)
        else:
            return self._run_cmd(self.client.play, idx)

    def toggle(self):
        """Toggle between playback / pause"""
        return self._run_cmd(self.client.pause)

    def pause(self):
        """Pause playback if playing

        This is what you want as card removal action: pause the playback, so it can be resumed when card is placed
        on the reader again. What happens on re-placement depends on configured second swipe option
        """
        return self._run_cmd(self.client.pause, 1)

    def stop(self):
        return self._run_cmd(self.client.stop)

    @plugin.tag
    def get_queue(self):
        return self._run_cmd(self.client.playlistinfo)

    # -----------------------------------------------------
    # Volume control (for developing only)

    async def _volume(self, value):
        return await self.client.setvol(value)

    @plugin.tag
    def set_volume(self, value):
        return asyncio.run_coroutine_threadsafe(self._volume(value), self.loop).result()

    # ----------------------------------
    # Stuff that replaces the current playlist and starts a new playback for URI

    @plugin.tag
    def play_uri(self, uri: str, **kwargs):
        """Decode URI and forward play call

        mpd:folder:path/to/folder
            --> Build playlist from $MUSICLIB_DIR/path/to/folder/*

        mpd:file:path/to/file.mp3
            --> Plays single file

        mpd:album:Feuerwehr:albumartist:Benjamin
          -> Searches MPD database for album Feuerwehr from artist Benjamin

        Conceptual at the moment (i.e. means it will likely change):
        mpd:podcast:path/to/file.yaml
          --> Reads local file: $PODCAST_FOLDER/path/to/file.yaml
          --> which contains: https://cool-stuff.de/podcast.xml

        mpd:livestream:path/to/file.yaml
          --> Reads local file: $LIVESTREAM_FOLDER/path/to/file.yaml
          --> which contains: https://hot-stuff.de/livestream.mp3
        Why go via a local file? We need to have a database with all podcasts that we can pull out and display
        to the user so he can select "play this one"

        """
        self.clear()
        # Clear the active uri before retrieving the track list, to avoid stale active uri in case something goes wrong
        self._active_uri = ''
        tracklist = self.get_from_uri(uri, **kwargs)
        self._active_uri = uri
        self.enqueue(tracklist)
        self._restore_state()
        self.play()

    def clear(self):
        return self._run_cmd(self.client.clear)

    async def _enqueue(self, tracklist):
        for entry in tracklist:
            path = entry.get('file')
            if path is not None:
                await self.client.add(path)

    def enqueue(self, tracklist):
        return asyncio.run_coroutine_threadsafe(self._enqueue(tracklist), self.loop).result()

    # ----------------------------------
    # Get track lists

    @plugin.tag
    def get_from_uri(self, uri: str, **kwargs):
        player_type, list_type, path = uri.split(':', 2)
        if player_type != 'mpd':
            raise KeyError(f"URI prefix must be 'mpd' not '{player_type}")
        func = self._flavors.get(list_type)
        if func is None:
            raise KeyError(f"URI flavor '{list_type}' unknown. Must be one of: {self._flavors.keys()}.")
        return func(path, **kwargs)

    @plugin.tag
    def get_files(self, path, recursive=False):
        """
        List file meta data for single file or all files of folder

        :returns: List of file(s) and directories including meta data
        """
        path = sanitize(path)
        if os.path.isfile(path):
            files = self._run_cmd(self.client.find, 'file', path)
        elif not recursive:
            files = self._run_cmd(self.client.lsinfo, path)
        else:
            files = self._run_cmd(self.client.find, 'base', path)
        return files

    @plugin.tag
    def get_track(self, path):
        playlist = self._run_cmd(self.client.find, 'file', path)
        if len(playlist) != 1:
            raise ValueError(f"Path decodes to more than one file: '{path}'")
        file = playlist[0].get('file')
        if file is None:
            raise ValueError(f"Not a music file: '{path}'")
        return playlist

    # ----------------------------------
    # Get albums / album tracks

    @plugin.tag
    def get_albums(self):
        """Returns all albums in database"""
        # return asyncio.run_coroutine_threadsafe(self._get_albums(), self.loop).result()
        return self._run_cmd(self.client.list, 'album', 'group', 'albumartist')

    @plugin.tag
    def get_album_tracks(self, album_artist, album):
        """Returns all songs of an album"""
        return self._run_cmd(self.client.find, 'albumartist', album_artist, 'album', album)

    def get_album_from_uri(self, uri: str):
        """Accepts full or partial uri (partial means without leading 'mpd:')"""
        p = re.match(r"(mpd:)?album:(.*):albumartist:(.*)", uri)
        if not p:
            raise ValueError(f"Cannot decode album and/or album artist from URI: '{uri}'")
        return self.get_album_tracks(album_artist=p.group(3), album=p.group(2))

    # ----------------------------------
    # Get podcasts / livestreams

    def _get_podcast_items(self, path):
        """Decode playlist of one podcast file"""
        pass

    @plugin.tag
    def get_podcast(self, path):
        """
        If :attr:`path is a

            * directory: List all stored podcasts in directory
            * file: List podcast playlist

        """
        pass

    def _get_livestream_items(self, path):
        """Decode playlist of one livestream file"""
        pass

    @plugin.tag
    def get_livestream(self, path):
        """
        If :attr:`path is a

            * directory: List all stored livestreams in directory
            * file: List livestream playlist

        """
        pass

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
