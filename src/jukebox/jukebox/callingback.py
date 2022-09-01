# RPi-Jukebox-RFID Version 3
# Copyright (c) See file LICENSE in project root folder
"""
Provides a generic callback handler
"""
import logging
import threading
import traceback
from typing import Callable, Optional, List


class CallbackHandler:
    """
    Generic Callback Handler to collect callbacks functions through :func:`register` and execute them
    with :func:`run_callbacks`

    A lock is used to sequence registering of new functions and running callbacks.

    :param name: A name of this handler for usage in log messages
    :param logger: The logger instance to use for logging
    :param context: A custom context handler to use as lock. If none, a local :class:`threading.Lock()` will be created
    """

    def __init__(self, name: str, logger: logging.Logger, context=None):
        self._callbacks: List[Callable[..., None]] = []
        self._name = name
        self._logger = logger
        self._context = context if context is not None else threading.Lock()

    def register(self, func: Optional[Callable[..., None]]):
        """Register a new function to be executed when the callback event happens

        :param func: The function to register. If set to :data:`None`, this register request is silently ignored."""
        with self._context:
            if func is not None:
                if callable(func):
                    self._callbacks.append(func)
                else:
                    self._logger.error(f"In callback handler '{self._name}' while registering new callback. "
                                       f"Not a callable: '{func.__qualname__}'")

    def _run_callbacks(self, *args, **kwargs):
        """Run all callbacks w/o acquiring the context first.

        Comes in useful in scenarios where the calling function has already acquired the context.
        """
        for f in self._callbacks:
            try:
                f(*args, **kwargs)
            except Exception:
                self._logger.error(f"In callback handler '{self._name}': while executing callback '{f.__qualname__}': \n"
                                   f"{traceback.format_exc()}")

    def run_callbacks(self, *args, **kwargs):
        """Run all registered callbacks.

        *ALL* exceptions from callback functions will be caught and logged only.
        Exceptions are not raised upwards! """
        with self._context:
            self._run_callbacks(*args, **kwargs)

    @property
    def has_callbacks(self):
        """:data:`True` if there are any registered callbacks. Read-only property"""
        return len(self._callbacks) > 0
