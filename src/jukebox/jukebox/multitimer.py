"""MultiTimer Module

This module provides timer functionality with support for single, multiple, and endless iterations.
It includes three main timer classes:
- MultiTimer: The base timer implementation using threading
- GenericTimerClass: A single-event timer with plugin/RPC support
- GenericEndlessTimerClass: An endless repeating timer
- GenericMultiTimerClass: A multi-iteration timer with callback builder support

Example usage:
    # Single event timer
    timer = GenericTimerClass("my_timer", 5.0, my_function)
    timer.start()

    # Endless timer
    endless_timer = GenericEndlessTimerClass("endless", 1.0, update_function)
    endless_timer.start()

    # Multi-iteration timer
    multi_timer = GenericMultiTimerClass("counter", 5, 1.0, CounterCallback)
    multi_timer.start()
"""

import threading
from typing import Callable, Optional, Any, Dict
import logging
import jukebox.cfghandler
import jukebox.plugs as plugin
import jukebox.publishing as publishing
from time import time


logger = logging.getLogger('jb.multitimers')
cfg = jukebox.cfghandler.get_handler('jukebox')


class MultiTimer(threading.Thread):
    """A threaded timer that calls a function after specified intervals.

    This timer supports both limited iterations and endless execution modes.
    In limited iteration mode, it counts down from iterations-1 to 0.
    In endless mode (iterations < 0), it runs indefinitely until cancelled.

    The timer can be cancelled at any time using the cancel() method.

    Attributes:
        interval (float): Time in seconds between function calls
        iterations (int): Number of times to call the function. Use negative for endless mode
        function (Callable): Function to call on each iteration
        args (list): Positional arguments to pass to the function
        kwargs (dict): Keyword arguments to pass to the function
        publish_callback (Optional[Callable]): Function to call on timer start/stop for state publishing

    Example:
        def my_func(iteration, x, y=10):
            print(f"Iteration {iteration}: {x} + {y}")

        timer = MultiTimer(2.0, 5, my_func, args=[5], kwargs={'y': 20})
        timer.start()
    """

    def __init__(self, interval: float, iterations: int, function: Callable, args=None, kwargs=None):
        """Initialize the timer.

        Args:
            interval: Seconds between function calls
            iterations: Number of iterations (-1 for endless)
            function: Function to call each iteration
            args: Positional arguments for function
            kwargs: Keyword arguments for function
        """
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
        self._cmd_cancel = True
        self.event.set()

    def trigger(self):
        """Trigger the next function call immediately."""
        self.event.set()

    def run_endless(self):
        """Run the timer in endless mode.

        The function is called every interval seconds with iteration=-1
        until cancelled.
        """
        while True:
            self.event.wait(self.interval)
            if self.event.is_set():
                if self._cmd_cancel:
                    break
                else:
                    self.event.clear()
            self.function(iteration=-1, *self.args, **self.kwargs)

    def run_limited(self):
        """Run the timer for a limited number of iterations.

        The function is called every interval seconds with iteration
        counting down from iterations-1 to 0.
        """
        for iteration in range(self.iterations - 1, -1, -1):
            self.event.wait(self.interval)
            if self.event.is_set():
                if self._cmd_cancel:
                    break
                else:
                    self.event.clear()
            self.function(*self.args, iteration=iteration, **self.kwargs)

    def run(self):
        """Start the timer execution.

        This is called automatically when start() is called.
        The timer runs in either endless or limited mode based on
        the iterations parameter.
        """
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
    """A single-event timer with plugin/RPC support.

    This class provides a high-level interface for creating and managing
    single-execution timers. It includes support for:
    - Starting/stopping/toggling the timer
    - Publishing timer state
    - Getting remaining time
    - Adjusting timeout duration

    The timer automatically handles the 'iteration' parameter internally,
    so callback functions don't need to handle it.

    Attributes:
        name (str): Identifier for the timer
        _wait_seconds (float): Interval between function calls
        _function (Callable): Wrapped function to call
        _iterations (int): Number of iterations (1 for single-event)

    Example:
        def update_display(message):
            print(message)

        timer = GenericTimerClass("display_timer", 5.0, update_display,
                                args=["Hello World"])
        timer.start()
    """

    def __init__(self, name: str, wait_seconds: float, function: Callable,
                 args: Optional[list] = None, kwargs: Optional[dict] = None):
        """Initialize the timer.

        Args:
            name: Timer identifier
            wait_seconds: Time to wait before function call
            function: Function to call
            args: Positional arguments for function
            kwargs: Keyword arguments for function
        """
        self.timer_thread = None
        self.args = args if args is not None else []
        self.kwargs = kwargs if kwargs is not None else {}
        self._wait_seconds = wait_seconds
        self._start_time = 0
        # Hide away the argument 'iteration' that is passed from MultiTimer to function
        self._function = lambda iteration, *largs, **lkwargs: function(*largs, **lkwargs)
        self._iterations = 1
        self._name = name
        self._publish_core()

    @plugin.tag
    def start(self, wait_seconds: Optional[float] = None):
        """Start the timer with optional new wait time.

        Args:
            wait_seconds: Optional new interval to use
        """
        if self.is_alive():
            logger.info(f"Timer '{self._name}' started! Ignoring start command.")
            return
        if wait_seconds is not None:
            self._wait_seconds = wait_seconds
        self.timer_thread = MultiTimer(self._wait_seconds, self._iterations,
                                     self._function, self.args, self.kwargs)
        self.timer_thread.daemon = True
        self.timer_thread.publish_callback = self._publish_core
        if self._name is not None:
            self.timer_thread.name = self._name
        self._start_time = int(time())
        self.timer_thread.start()

    @plugin.tag
    def cancel(self):
        """Cancel the timer if it's running."""
        if self.is_alive():
            self.timer_thread.cancel()

    @plugin.tag
    def toggle(self):
        """Toggle between started and stopped states."""
        if self.is_alive():
            self.timer_thread.cancel()
        else:
            self.start()

    @plugin.tag
    def trigger(self):
        """Trigger the function call immediately."""
        if self.is_alive():
            self.timer_thread.trigger()

    @plugin.tag
    def is_alive(self) -> bool:
        """Check if timer is currently running.

        Returns:
            bool: True if timer is active, False otherwise
        """
        if self.timer_thread is None:
            return False
        return self.timer_thread.is_alive()

    @plugin.tag
    def get_timeout(self) -> float:
        """Get the configured timeout interval.

        Returns:
            float: The wait time in seconds
        """
        return self._wait_seconds

    @plugin.tag
    def set_timeout(self, wait_seconds: float) -> float:
        """Set a new timeout interval.

        If the timer is running, it will be restarted with the new interval.

        Args:
            wait_seconds: New interval in seconds

        Returns:
            float: The new wait time
        """
        self._wait_seconds = wait_seconds
        if self.is_alive():
            self.cancel()
            self.start()
        else:
            self.publish()
        return self._wait_seconds

    @plugin.tag
    def publish(self):
        """Publish current timer state."""
        self._publish_core()

    @plugin.tag
    def get_state(self) -> Dict[str, Any]:
        """Get the current timer state.

        Returns:
            dict: Timer state including:
                - enabled: Whether timer is running
                - remaining_seconds: Time until next function call
                - wait_seconds: Configured interval
                - type: Timer class name
        """
        remaining_seconds = max(
            0,
            self.get_timeout() - (int(time()) - self._start_time)
        )

        return {
            'enabled': self.is_alive(),
            'remaining_seconds': remaining_seconds,
            'wait_seconds': self.get_timeout(),
            'type': 'GenericTimerClass'
        }

    def _publish_core(self, enabled: Optional[bool] = None):
        """Internal method to publish timer state.

        Args:
            enabled: Override for enabled state
        """
        if self._name is not None:
            state = self.get_state()
            if enabled is not None:
                state['enabled'] = enabled
            logger.debug(f"{self._name}: State = {state}")
            publishing.get_publisher().send(self._name, state)


class GenericEndlessTimerClass(GenericTimerClass):
    """An endless repeating timer.

    This timer runs indefinitely until explicitly cancelled.
    It inherits all functionality from GenericTimerClass but
    sets iterations to -1 for endless mode.

    Example:
        def heartbeat():
            print("Ping")

        timer = GenericEndlessTimerClass("heartbeat", 1.0, heartbeat)
        timer.start()
    """

    def __init__(self, name: str, wait_seconds_per_iteration: float,
                 function: Callable, args=None, kwargs=None):
        """Initialize endless timer.

        Args:
            name: Timer identifier
            wait_seconds_per_iteration: Interval between calls
            function: Function to call repeatedly
            args: Positional arguments for function
            kwargs: Keyword arguments for function
        """
        super().__init__(name, wait_seconds_per_iteration, function, args, kwargs)
        # Negative iteration count causes endless looping
        self._iterations = -1

    @plugin.tag
    def get_state(self) -> Dict[str, Any]:
        """Get current timer state.

        Returns:
            dict: Timer state including:
                - enabled: Whether timer is running
                - wait_seconds_per_iteration: Interval between calls
                - type: Timer class name
        """
        return {
            'enabled': self.is_alive(),
            'wait_seconds_per_iteration': self.get_timeout(),
            'type': 'GenericEndlessTimerClass'
        }


class GenericMultiTimerClass(GenericTimerClass):
    """A multi-iteration timer with callback builder support.

    This timer executes a specified number of iterations with a callback
    that's created for each full cycle. It's useful when you need stateful
    callbacks or complex iteration handling.

    The callee parameter should be a class or function that:
    1. Takes iterations as a parameter during construction
    2. Returns a callable that accepts an iteration parameter

    Example:
        class CountdownCallback:
            def __init__(self, iterations):
                self.total = iterations

            def __call__(self, iteration):
                print(f"{iteration} of {self.total} remaining")

        timer = GenericMultiTimerClass("countdown", 5, 1.0, CountdownCallback)
        timer.start()
    """

    def __init__(self, name: str, iterations: int, wait_seconds_per_iteration: float,
                 callee: Callable, args=None, kwargs=None):
        """Initialize multi-iteration timer.

        Args:
            name: Timer identifier
            iterations: Total number of iterations
            wait_seconds_per_iteration: Interval between calls
            callee: Callback builder class/function
            args: Positional arguments for callee
            kwargs: Keyword arguments for callee
        """
        # Initialize with a placeholder function - we'll set the real one in start()
        super().__init__(name, wait_seconds_per_iteration, lambda: None, None, None)
        self.class_args = args if args is not None else []
        self.class_kwargs = kwargs if kwargs is not None else {}
        self._iterations = iterations
        self._callee = callee

    @plugin.tag
    def start(self, iterations: Optional[int] = None,
              wait_seconds_per_iteration: Optional[float] = None):
        """Start the timer with optional new parameters.

        Args:
            iterations: Optional new iteration count
            wait_seconds_per_iteration: Optional new interval
        """
        if iterations is not None:
            self._iterations = iterations

        def create_callback():
            instance = self._callee(*self.class_args, iterations=self._iterations,
                                  **self.class_kwargs)
            return lambda iteration, *args, **kwargs: instance(*args,
                                                             iteration=iteration,
                                                             **kwargs)

        self._function = create_callback()
        super().start(wait_seconds_per_iteration)

    @plugin.tag
    def get_state(self) -> Dict[str, Any]:
        """Get current timer state.

        Returns:
            dict: Timer state including:
                - enabled: Whether timer is running
                - wait_seconds_per_iteration: Interval between calls
                - remaining_seconds_current_iteration: Time until next call
                - remaining_seconds: Total time remaining
                - iterations: Total iteration count
                - type: Timer class name
        """
        remaining_seconds_current_iteration = max(
            0,
            self.get_timeout() - (int(time()) - self._start_time)
        )
        remaining_seconds = (self.get_timeout() * self._iterations + remaining_seconds_current_iteration)

        return {
            'enabled': self.is_alive(),
            'wait_seconds_per_iteration': self.get_timeout(),
            'remaining_seconds_current_iteration': remaining_seconds_current_iteration,
            'remaining_seconds': remaining_seconds,
            'iterations': self._iterations,
            'type': 'GenericMultiTimerClass'
        }
