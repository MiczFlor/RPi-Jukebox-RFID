from enum import Enum
from typing import Callable, Generic, TypeVar

from jukebox.callingback import CallbackHandler


class PlayCardState(Enum):
    FIRST_SWIPE = 0
    SECOND_SWIPE = 1


STATE = TypeVar('STATE', bound=Enum)


class PlayContentCallbacks(Generic[STATE], CallbackHandler):
    """
    Callbacks are executed in various play functions
    """

    def register(self, func: Callable[[str, STATE], None]):
        """
        Add a new callback function :attr:`func`.

        Callback signature is

        .. py:function:: func(folder: str, state: STATE)
            :noindex:

        :param folder: relative path to folder to play
        :param state: indicator of the state inside the calling
        """
        super().register(func)

    def run_callbacks(self, folder: str, state: STATE):
        """:meta private:"""
        super().run_callbacks(folder, state)
