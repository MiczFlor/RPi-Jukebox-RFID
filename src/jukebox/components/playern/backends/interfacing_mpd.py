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
    return path.lstrip('./')


class MPDBackend:

    def __init__(self, event_loop):
        self.client = MPDClient()
        self.loop = event_loop
        self.host = 'localhost'
        self.port = '6600'
        self._flavors = {'folder': self.play_folder,
                         'album': self.play_album_uri,
                         'albumartist': self.play_album_artist_uri,
                         'file': self.play_file,
                         'podcast': self.play_podcast,
                         'livestream': self.play_livestream}
        # TODO: If connect fails on first try this is non recoverable
        self.connect()
        # Start the status listener in an endless loop in the event loop
        asyncio.run_coroutine_threadsafe(self._status_listener(), self.loop)

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

    async def _next(self):
        return await self.client.next()

    def next(self):
        logger.debug('Next')
        return asyncio.run_coroutine_threadsafe(self._next(), self.loop).result()

    async def _prev(self):
        return await self.client.next()

    def prev(self):
        return asyncio.run_coroutine_threadsafe(self._prev(), self.loop).result()

    async def _stop(self):
        return await self.client.stop()

    def stop(self):
        return asyncio.run_coroutine_threadsafe(self._stop(), self.loop).result()

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

        mpd:podcast:path/to/file.yaml
          --> Reads local file: $PODCAST_FOLDER/path/to/file.yaml
          --> which contains: https://cool-stuff.de/podcast.xml

        mpd:livestream:path/to/file.yaml
          --> Reads local file: $LIVESTREAM_FOLDER/path/to/file.yaml
          --> which contains: https://hot-stuff.de/livestream.mp3
        Why go via a local file? We need to have a database with all podcasts that we can pull out and display
        to the user so he can select "play this one"

        """
        player_type, list_type, path = uri.split(':', 2)
        if player_type != 'mpd':
            raise KeyError(f"URI prefix must be 'mpd' not '{player_type}")
        func = self._flavors.get(list_type)
        if func is None:
            raise KeyError(f"URI flavor '{list_type}' unknown. Must be one of: {self._flavors.keys()}.")
        return func(path, **kwargs)

    def play_folder(self, path, recursive=False):
        logger.debug(f"Play folder: {path}")
        # MPD command to get files in folder non-recursive: client.lsinfo('Conni')
        # MPD command to get files in folder recursive: client.find('base', 'Conni')
        pass

    def play_file(self, path):
        pass

    def play_album(self, album_artist: str, album: str):
        # MPD command client.findadd('albumartist', albumartist, 'album', album)
        pass

    def play_album_uri(self, uri: str):
        p = re.match(r"album:(.*):albumartist:(.*)", uri)
        if p:
            album = p.group(1)
            album_artist = p.group(2)
            self.play_album(album_artist=album_artist, album=album)
        else:
            raise ValueError(f"Cannot decode album and/or album artist from URI: '{uri}'")

    def play_album_artist_uri(self, uri: str):
        p = re.match(r"albumartist:(.*):album:(.*)", uri)
        if p:
            album = p.group(2)
            album_artist = p.group(1)
            self.play_album(album_artist=album_artist, album=album)
        else:
            raise ValueError(f"Cannot decode album and/or album artist from URI: '{uri}'")

    def play_podcast(self, path):
        # If uri == file, decode and play all entries
        # If uri == folder, decode and play all files?
        pass

    def play_livestream(self, path):
        pass

    # ----------------------------------
    # Get track lists

    async def _get_single_file(self, path):
        return await self.client.find('file', path)

    async def _get_folder_recursive(self, path):
        return await self.client.find('base', path)

    async def _get_folder(self, path):
        return await self.client.lsinfo(path)

    @plugin.tag
    def get_files(self, path, recursive=False):
        """
        List file meta data for single file or all files of folder

        :returns: List of file(s) and directories including meta data
        """
        path = sanitize(path)
        if os.path.isfile(path):
            files = asyncio.run_coroutine_threadsafe(self._get_single_file(path), self.loop).result()
        elif not recursive:
            files = asyncio.run_coroutine_threadsafe(self._get_folder(path), self.loop).result()
        else:
            files = asyncio.run_coroutine_threadsafe(self._get_folder_recursive(path), self.loop).result()
        return files

    # ----------------------------------
    # Get albums / album tracks

    async def _get_albums(self):
        return await self.client.list('album', 'group', 'albumartist')

    @plugin.tag
    def get_albums(self):
        """Returns all albums in database"""
        return asyncio.run_coroutine_threadsafe(self._get_albums(), self.loop).result()

    async def _get_album_tracks(self, album_artist, album):
        return await self.client.find('albumartist', album_artist, 'album', album)

    @plugin.tag
    def get_album_tracks(self, album_artist, album):
        """Returns all song of an album"""
        return asyncio.run_coroutine_threadsafe(self._get_album_tracks(album_artist, album), self.loop).result()

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

    # ----------------------------------
    # Conceptual

    def get_uri(self, uri, **kwargs):
        """Maps to get_* depending on URI prefix?"""
        pass

    # -----------------------------------------------------
    # Queue / URI state  (save + restore e.g. random, resume, ...)

    def save_uri_state(self):
        """Save the configuration and state of the current URI playback to the URIs state file"""
        pass
