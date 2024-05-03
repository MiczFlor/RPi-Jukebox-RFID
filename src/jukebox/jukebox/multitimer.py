# RPi-Jukebox-RFID Version 3
# Copyright (c) See file LICENSE in project root folder

"""Multitimer Module"""

import threading
from typing import (
    Callable)
import logging
import jukebox.cfghandler
import jukebox.plugs as plugin
import jukebox.publishing as publishing
from time import time


logger = logging.getLogger('jb.multitimers')
cfg = jukebox.cfghandler.get_handler('jukebox')


class MultiTimer(threading.Thread):
    """Call a function after a specified number of seconds, repeat that iteration times

    May be cancelled during any of the wait times.
    Function is called with keyword parameter 'iteration' (which decreases down to 0 for the last iteration)

    If iterations is negative, an endlessly repeating timer is created (which needs to be cancelled with cancel())

    Initiates start and publishing by calling self.publish_callback

    Note: Inspired by threading.Timer and generally using the same API"""

    def __init__(self, interval, iterations, function: Callable, args=None, kwargs=None):
        super().__init__()
        self.interval = interval
        self.iterations = iterations
        self.function = function
        self.args = args if args is not None else []
        self.kwargs = kwargs if kwargs is not None else {}
        self.event = threading.Event()
        self.publish_callback = None
        self._cmd_cancel = False

    def cancel(self):
        """Stop the timer if it hasn't finished all iterations yet."""
        logger.debug(f"Cancel timer '{self.name}.")
        # Assignment to _cmd_cancel is atomic -> OK for threads
        self._cmd_cancel = True
        self.event.set()

    def trigger(self):
        self.event.set()

    def run_endless(self):
        while True:
            self.event.wait(self.interval)
            if self.event.is_set():
                if self._cmd_cancel:
                    break
                else:
                    self.event.clear()
            # logger.debug(f"Execute timer action of '{self.name}'.")
            self.function(iteration=-1, *self.args, **self.kwargs)

    def run_limited(self):
        for iteration in range(self.iterations - 1, -1, -1):
            self.event.wait(self.interval)
            if self.event.is_set():
                if self._cmd_cancel:
                    break
                else:
                    self.event.clear()
            # logger.debug(f"Execute timer action #{iteration} of '{self.name}'.")
            self.function(*self.args, iteration=iteration, **self.kwargs)

    def run(self):
        if self.publish_callback is not None:
            self.publish_callback()
        if self.iterations < 0:
            logger.debug(f"Start timer '{self.name} in endless mode")
            self.run_endless()
        else:
            logger.debug(f"Start timer '{self.name} with {self.iterations} iterations")
            self.run_limited()
        self._cmd_cancel = True
        self.event.set()
        if self.publish_callback is not None:
            self.publish_callback(enabled=False)


class GenericTimerClass:
    """
    Interface for plugin / RPC accessibility for a single event timer
    """
    def __init__(self, name, wait_seconds: float, function, args=None, kwargs=None):
        """
        :param wait_seconds: The time in seconds to wait before calling function
        :param function: The function to call with args and kwargs.
        :param args: Parameters for function call
        :param kwargs: Parameters for function call
        """
        self.timer_thread = None
        self.args = args if args is not None else []
        self.kwargs = kwargs if kwargs is not None else {}
        self._wait_seconds = wait_seconds
        self._start_time = 0
        # Hide away the argument 'iteration' that is passed from MultiTimer to function
        # for a single event Timer (and also endless timers, as the inherit from here)
        self._function = lambda iteration, *largs, **lkwargs: function(*largs, **lkwargs)
        self._iterations = 1
        self._name = name
        self._publish_core()

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
        self.timer_thread.publish_callback = self._publish_core
        if self._name is not None:
            self.timer_thread.name = self._name
        self._start_time = int(time())
        self.timer_thread.start()

    @plugin.tag
    def cancel(self):
        """Cancel the timer"""
        if self.is_alive():
            self.timer_thread.cancel()

    @plugin.tag
    def toggle(self):
        """Toggle the activation of the timer"""
        if self.is_alive():
            self.timer_thread.cancel()
        else:
            self.start()

    @plugin.tag
    def trigger(self):
        """Trigger the next target execution before the time is up"""
        if self.is_alive():
            self.timer_thread.trigger()

    @plugin.tag
    def is_alive(self):
        """Check if timer is active"""
        if self.timer_thread is None:
            return False
        return self.timer_thread.is_alive()

    @plugin.tag
    def get_timeout(self):
        """Get the configured time-out

        :return: The total wait time. (Not the remaining wait time!)"""
        return self._wait_seconds

    @plugin.tag
    def set_timeout(self, wait_seconds: float):
        """Set a new time-out in seconds. Re-starts the timer if already running!"""
        self._wait_seconds = wait_seconds
        if self.is_alive():
            self.cancel()
            self.start()
        else:
            self.publish()
        return self._wait_seconds

    @plugin.tag
    def publish(self):
        """Publish the current state and config"""
        self._publish_core()

    @plugin.tag
    def get_state(self):
        """Get the current state and config as dictionary"""
        remaining_seconds = max(
            0,
            self.get_timeout() - (int(time()) - self._start_time)
        )

        return {'enabled': self.is_alive(),
                'remaining_seconds': remaining_seconds,
                'wait_seconds': self.get_timeout(),
                'type': 'GenericTimerClass'}

    def _publish_core(self, enabled=None):
        """Internal publish function with override for enabled

        Enable override is required as this is called from inside the timer when it finishes
        This means the timer is still running, but it is the last thing it does.
        Otherwise it is not possible to detect the timer change at the end"""
        if self._name is not None:
            state = self.get_state()
            if enabled is not None:
                state['enabled'] = enabled
            logger.debug(f"{self._name}: State = {state}")
            # This function may be called from different threads,
            # so always freshly get the correct publisher instance
            publishing.get_publisher().send(self._name, state)


class GenericEndlessTimerClass(GenericTimerClass):
    """
    Interface for plugin / RPC accessibility for an event timer call function endlessly every m seconds
    """
    def __init__(self, name, wait_seconds_per_iteration: float, function, args=None, kwargs=None):
        # Remove the necessity for the 'iterations' keyword that is added by GenericTimerClass
        super().__init__(name, wait_seconds_per_iteration, function, args, kwargs)
        # Negative iteration count causes endless looping
        self._iterations = -1

    def get_state(self):
        return {'enabled': self.is_alive(),
                'wait_seconds_per_iteration': self.get_timeout(),
                'type': 'GenericEndlessTimerClass'}


class GenericMultiTimerClass(GenericTimerClass):
    """
    Interface for plugin / RPC accessibility for an event timer that performs an action n times every m seconds
    """
    def __init__(self, name, iterations: int, wait_seconds_per_iteration: float, callee, args=None, kwargs=None):
        """
        :param iterations: Number of times callee is called
        :param wait_seconds_per_iteration: Wait in seconds before each iteration
        :param callee: A builder class that gets instantiated once as callee(*args, iterations=iterations, **kwargs).
        Then with every time out iteration __call__(*args, iteration=iteration, **kwargs) is called.
        'iteration' is the current iteration count in decreasing order!
        :param args:
        :param kwargs:
        """
        super().__init__(name, wait_seconds_per_iteration, None, None, None)
        self.class_args = args if args is not None else []
        self.class_kwargs = kwargs if kwargs is not None else {}
        self._iterations = iterations
        self._callee = callee

    @plugin.tag
    def start(self, iterations=None, wait_seconds_per_iteration=None):
        """Start the timer (with default or new parameters)"""
        if iterations is not None:
            self._iterations = iterations
        self._function = self._callee(*self.class_args, iterations=self._iterations, **self.class_kwargs)
        super().start(wait_seconds_per_iteration)

    @plugin.tag
    def get_state(self):
        return {'enabled': self.is_alive(),
                'wait_seconds_per_iteration': self.get_timeout(),
                'iterations': self._iterations,
                'type': 'GenericMultiTimerClass'}
