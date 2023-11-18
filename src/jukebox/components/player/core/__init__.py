# Copyright: 2022
# SPDX License Identifier: MIT License

"""
Top-level player control across all player backends

Usage concept:

# Stuff to control playback
player.ctrl.play(...)
player.ctrl.next()

# To get MPD specific playlists
player.mpd.get_album(...)
player.mpd.get_...(...)

"""

import logging
from typing import Dict, Callable, Optional, Any

import jukebox.plugs as plugin

logger = logging.getLogger('jb.player')


class PlayerCtrl:
    """The top-level player instance through which all calls go. Arbitrates between the different backends"""

    def __init__(self):
        self._backends: Dict[str, Any] = {}
        self._active = None

    def register(self, name: str, backend):
        self._backends[name] = backend
        # For now simply default to first registered backend
        if self._active is None:
            self._active = self._backends.values().__iter__().__next__()

    @plugin.tag
    def get_active(self):
        name = 'None'
        for n, b in self._backends.items():
            if self._active == b:
                name = n
                break
        return name

    @plugin.tag
    def list_backends(self):
        logger.debug(f"Backend list: {self._backends.items()}")
        return [b for b in self._backends.keys()]

    @plugin.tag
    def play_uri(self, uri, check_second_swipe=False, **kwargs):
        # Save the current state and stop the current playback
        self.stop()
        # Decode card second swipe (TBD)
        # And finally play
        try:
            player_type, _ = uri.split(':', 1)
        except ValueError:
            raise ValueError(f"Malformed URI: {uri}")
        inst = self._backends.get(player_type)
        if inst is None:
            raise KeyError(f"URI player type unknown: '{player_type}'. Available backends are: {self._backends.keys()}.")
        self._active = self._backends.get(player_type)
        self._active.play_uri(uri, **kwargs)

    def _is_second_swipe(self):
        """
        Check if play request is a second swipe

        Definition second swipe:
            successive swipes of the same registered ID card

        A second swipe triggers a different action than the first swipe. In certain scenarios a second
        swipe needs to be treated as a first swipe:

            * if playlist has stopped playing
                * playlist has run out
                * playlist was stopped by trigger
            * if in a place-not-swipe setup, the card remains on reader until playlist expires and player enters state stop.
              Card is the removed and triggers 'card removal action' on stopped playlist. Card is placed on reader
              again and must be treated as first swipe
            * after reboot when last state is restored (first swipe is play which starts from the beginning or resumes,
              depending on playlist configuration)

        Second swipe actions can be

            * toggle
            * ignore (do nothing)
            * next
            * restart playlist --> is always like first swipe?

        """
        pass

    @plugin.tag
    def next(self):
        self._active.next()

    @plugin.tag
    def prev(self):
        self._active.prev()

    @plugin.tag
    def play(self):
        self._active.play()

    @plugin.tag
    def play_single(self, uri):
        self.play_uri(uri)

    @plugin.tag
    def toggle(self):
        self._active.toggle()

    @plugin.tag
    def pause(self):
        self._active.pause()

    @plugin.tag
    def stop(self):
        # Save current state for resume functionality
        self._save_state()
        self._active.stop()

    @plugin.tag
    def get_queue(self):
        self._active.get_queue()

    @plugin.tag
    def repeatmode(self):
        self._active.repeatmode()

    @plugin.tag
    def seek(self):
        self._active.seek()

    @plugin.tag
    def list_albums(self):
        """
        Coolects from every backend the albums and albumartists
        """
        album_list = []
        for name, bkend in self._backends.items():
            album_list.append(bkend.get_albums())

        return album_list

    @plugin.tag
    def list_song_by_artist_and_album(self, artist, albumname):
        for name, bkend in self._backends.items():
            s_item = filter(lambda album: album['artist'] == artist and album['albumname'] == albumname, bkend.get_albums())
        return s_item if s_item else None

    def _save_state(self):
        # Get the backend to save the state of the current playlist to the URI's config file
        self._active.save_state()
        # Also need to save which backend and URI was currently playing to be able to restore it after reboot
        pass
