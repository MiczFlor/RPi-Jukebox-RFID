# MIT License
#
# Copyright (c) 2021 Christian Banz
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#
# Contributing author(s):
# - Christian Banz

import threading
from typing import (
    Callable)
import logging
import jukebox.cfghandler
import jukebox.plugs as plugin


logger = logging.getLogger('jb.multitimers')
cfg = jukebox.cfghandler.get_handler('jukebox')


class MultiTimer(threading.Thread):
    """Call a function after a specified number of seconds, repeat that iteration times

    May be cancelled during any of the wait times.
    Function is called with keyword parameter 'iteration' (which decreases down to 0 for the last iteration)

    If iterations is negative, an endlessly repeating timer is created (which needs to be cancelled with cancel())

    Note: Inspired by threading.Timer and generally using the same API"""

    def __init__(self, interval, iterations, function: Callable, args=None, kwargs=None):
        super().__init__()
        self.interval = interval
        self.iterations = iterations
        self.function = function
        self.args = args if args is not None else []
        self.kwargs = kwargs if kwargs is not None else {}
        self.finished = threading.Event()

    def cancel(self):
        """Stop the timer if it hasn't finished all iterations yet."""
        logger.debug(f"Cancel timer '{self.name}.")
        self.finished.set()

    def run_endless(self):
        while True:
            self.finished.wait(self.interval)
            if not self.finished.is_set():
                # logger.debug(f"Execute timer action of '{self.name}'.")
                self.function(iteration=-1, *self.args, **self.kwargs)
            else:
                break

    def run_limited(self):
        for iteration in range(self.iterations - 1, -1, -1):
            self.finished.wait(self.interval)
            if not self.finished.is_set():
                # logger.debug(f"Execute timer action #{iteration} of '{self.name}'.")
                self.function(iteration=iteration, *self.args, **self.kwargs)
            else:
                break

    def run(self):
        if self.iterations < 0:
            logger.debug(f"Start timer '{self.name} in endless mode")
            self.run_endless()
        else:
            logger.debug(f"Start timer '{self.name} with {self.iterations} iterations")
            self.run_limited()
        self.finished.set()


class GenericTimerClass:
    """
    Interface for plugin / RPC accessibility for a single event timer
    """
    def __init__(self, wait_seconds: float, function, args=None, kwargs=None):
        """
        :param wait_seconds: The time in seconds to wait before calling function
        :param function: The function to call with args and kwargs.
        Note that a keyword parameter iteration is passed to function (which is always 0).
        :param args: Parameters for function call
        :param kwargs: Parameters for function call
        """
        self.timer_thread = None
        self.args = args if args is not None else []
        self.kwargs = kwargs if kwargs is not None else {}
        self._wait_seconds = wait_seconds
        # TODO: Wrap function with generic logger call?
        self._function = function
        self._iterations = 1
        self._name = 'Unnamed'

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, new_name):
        self._name = new_name

    @plugin.tag
    def start(self, wait_seconds=None):
        """Start the timer (with default or new parameters)"""
        if self.is_alive():
            logger.error(f"Timer '{self._name}' started! Ignoring start command.")
            return
        if wait_seconds is not None:
            self._wait_seconds = wait_seconds
        self.timer_thread = MultiTimer(self._wait_seconds, self._iterations, self._function, *self.args, **self.kwargs)
        self.timer_thread.daemon = True
        if self._name != 'Unnamed':
            self.timer_thread.name = self._name
        self.timer_thread.start()

    @plugin.tag
    def cancel(self):
        """Cancel the timer"""
        if self.is_alive():
            self.timer_thread.cancel()

    @plugin.tag
    def is_alive(self):
        """Check if timer is active"""
        if self.timer_thread is None:
            return False
        return self.timer_thread.is_alive()

    @plugin.tag
    def get_timeout(self):
        """Get the configured time-out

        Note: This is the total wait time. Not the remaining wait time!"""
        return self._wait_seconds

    @plugin.tag
    def set_timeout(self, wait_seconds: float):
        """Set a new time-out in seconds. Re-starts the timer if already running!"""
        self._wait_seconds = wait_seconds
        if self.is_alive():
            self.cancel()
            self.start()
        return self._wait_seconds


class GenericEndlessTimerClass(GenericTimerClass):
    """
    Interface for plugin / RPC accessibility for an event timer call function endlessly every m seconds
    """
    def __init__(self, wait_seconds_per_iteration: float, function, args=None, kwargs=None):
        super().__init__(wait_seconds_per_iteration, function, args, kwargs)
        # Negative iteration count causes endless looping
        self._iterations = -1


class GenericMultiTimerClass(GenericTimerClass):
    """
    Interface for plugin / RPC accessibility for an event timer that performs an action n times every m seconds
    """
    def __init__(self, iterations: int, wait_seconds_per_iteration: float, callee, args=None, kwargs=None):
        """
        :param iterations: Number of times callee is called
        :param wait_seconds_per_iteration: Wait in seconds before each iteration
        :param callee: A class that gets instantiated once as callee(iterations, *args, **kwargs).
        Then with every time out iteration __call__(iteration) is called. iteration is the current iteration count
        in decreasing order!
        :param args:
        :param kwargs:
        """
        super().__init__(wait_seconds_per_iteration, None, None, None)
        self.class_args = args if args is not None else []
        self.class_kwargs = kwargs if kwargs is not None else {}
        self._iterations = iterations
        self._callee = callee

    @plugin.tag
    def start(self, iterations=None, wait_seconds_per_iteration=None):
        """Start the timer (with default or new parameters)"""
        if iterations is not None:
            self._iterations = iterations
        self._function = self._callee(self._iterations, *self.class_args, **self.class_kwargs)
        super().start(wait_seconds_per_iteration)
