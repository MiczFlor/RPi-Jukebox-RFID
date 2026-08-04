from enum import Enum
from typing import Callable, Generic, TypeVar

from jukebox.callingback import CallbackHandler


class PlayCardState(Enum):
    firstSwipe = 0,
    secondSwipe = 1


STATE = TypeVar('STATE', bound=Enum)


class PlayContentCallbacks(Generic[STATE], CallbackHandler):
    """Callbacks executed before card-triggered playback actions."""

    def register(self, func: Callable[[str, STATE], None]):
        """
        Register a callback with the signature ``callback(content, state)``.

        :param func: Callback to register
        """
        super().register(func)

    def run_callbacks(self, content: str, state: STATE):
        """:meta private:"""
        super().run_callbacks(content, state)
