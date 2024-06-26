import logging
import time
import jukebox.cfghandler
import jukebox.plugs as plugin
from jukebox.multitimer import GenericMultiTimerClass

logger = logging.getLogger('jb.timers')
cfg = jukebox.cfghandler.get_handler('jukebox')

class VolumeFadoutAndShutdown:
    def __init__(self, name, current_volume=100):
        self.timer = None
        self.name = name
        self.current_volume = current_volume
        self.iterations = None
        self.wait_seconds_per_iteration = None
        self.start_time = None  # Store the start time
        self.total_wait_seconds = None  # Store the total wait time

    def _calculate_fadeout_parameters(self, wait_seconds, step_size):
        """Calculate iterations and wait_seconds_per_iteration based on wait_seconds and step_size."""
        self.iterations = max(1, int(self.current_volume / step_size))  # Ensure at least one iteration
        self.wait_seconds_per_iteration = float(wait_seconds) / self.iterations
        self.total_wait_seconds = wait_seconds

    @plugin.tag
    def start(self, wait_seconds=None, step_size=3):
        """Start the volume fadeout and shutdown timer."""
        if wait_seconds is None or step_size is None:
            raise ValueError("Both wait_seconds and step_size must be provided")

        self._calculate_fadeout_parameters(wait_seconds, step_size)
        self.start_time = time()  # Record the start time

        self.timer = GenericMultiTimerClass(
            name=self.name,
            iterations=self.iterations,
            wait_seconds_per_iteration=self.wait_seconds_per_iteration,
            callee=lambda iterations: VolumeFadoutAndShutdownActionClass(iterations, step_size)
        )
        self.timer.start()

    @plugin.tag
    def cancel(self):
        """Cancel the volume fadeout and shutdown timer."""
        if self.timer and self.timer.is_alive():
            self.timer.cancel()

    @plugin.tag
    def get_state(self):
        """Get the current state of the volume fadeout and shutdown timer."""
        if not self.timer:
            return {}

        timer_state = self.timer.get_state()
        elapsed_time = time() - self.start_time
        remaining_total_seconds = max(0, self.total_wait_seconds - elapsed_time)

        return {
            **timer_state,
            'remaining_total_seconds': remaining_total_seconds,
            'total_wait_seconds': self.total_wait_seconds,
        }

class VolumeFadoutAndShutdownActionClass:
    def __init__(self, iterations, step_size):
        self.iterations = iterations
        self.step_size = step_size
        self.volume = plugin.call('volume', 'ctrl', 'get_volume')

    def __call__(self, iteration):
        self.volume -= self.step_size
        logger.debug(f"Decrease volume to {self.volume} (Iteration index {iteration}/{self.iterations - 1})")
        plugin.call_ignore_errors('volume', 'ctrl', 'set_volume', args=[int(self.volume)])
        if iteration == 0:
            logger.debug("Shut down from volume fade out")
            plugin.call_ignore_errors('host', 'shutdown')
