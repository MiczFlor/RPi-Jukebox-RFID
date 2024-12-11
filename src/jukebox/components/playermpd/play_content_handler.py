from enum import Enum, auto
from dataclasses import dataclass
from typing import Union, Optional, Callable, Protocol
import logging

from .play_content_callback import PlayCardState  # Add this import

logger = logging.getLogger('jb.PlayerMPD')


class PlayContentType(Enum):
    SINGLE = auto()
    ALBUM = auto()
    FOLDER = auto()


@dataclass
class PlayContent:
    """Represents playable content with its type and metadata"""
    type: PlayContentType
    content: Union[str, tuple[str, str]]  # str for SINGLE/FOLDER, tuple(artist, album) for ALBUM
    recursive: bool = False


class PlayerProtocol(Protocol):
    """Protocol defining required player methods"""
    def _play_single_internal(self, song_url: str) -> None:
        """Play a single track"""

    def _play_album_internal(self, artist: str, album: str) -> None:
        """Play an album"""

    def _play_folder_internal(self, folder: str, recursive: bool) -> None:
        """Play a folder"""

    @property
    def play_card_callbacks(self) -> any:
        """Access to callbacks"""


class PlayContentHandler:
    """Handles different types of playback content with second swipe support"""

    def __init__(self, player: PlayerProtocol):
        self.player = player
        self.last_played_content: Optional[PlayContent] = None
        self._second_swipe_action = None

    def set_second_swipe_action(self, action: Optional[Callable]) -> None:
        """Set the action to be performed on second swipe"""
        self._second_swipe_action = action

    def _play_content(self, content: PlayContent) -> None:
        """Internal method to play content based on its type"""
        if content.type == PlayContentType.SINGLE:
            logger.debug(f"Playing single track: {content.content}")
            self.player._play_single_internal(content.content)
        elif content.type == PlayContentType.ALBUM:
            artist, album = content.content
            logger.debug(f"Playing album: {album} by {artist}")
            self.player._play_album_internal(artist, album)
        elif content.type == PlayContentType.FOLDER:
            logger.debug(f"Playing folder: {content.content} (recursive={content.recursive})")
            self.player._play_folder_internal(content.content, content.recursive)

    def play_content(self, content: PlayContent) -> None:
        """
        Main entry point for playing content with second swipe support

        Checks for second trigger of the same content and calls first/second swipe
        action accordingly.
        """
        is_second_swipe = False

        if self.last_played_content is not None:
            if (content.type == self.last_played_content.type
                    and content.content == self.last_played_content.content):
                is_second_swipe = True

        if self._second_swipe_action is not None and is_second_swipe:
            logger.debug('Calling second swipe action')
            # run callbacks before second_swipe_action is invoked
            self.player.play_card_callbacks.run_callbacks(
                str(content.content),
                PlayCardState.secondSwipe  # Use imported PlayCardState directly
            )
            self._second_swipe_action()
        else:
            logger.debug('Calling first swipe action')
            # run callbacks before play_content is invoked
            self.player.play_card_callbacks.run_callbacks(
                str(content.content),
                PlayCardState.firstSwipe  # Use imported PlayCardState directly
            )
            self._play_content(content)

        self.last_played_content = content
