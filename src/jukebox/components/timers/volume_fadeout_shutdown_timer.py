import logging
import time
import jukebox.cfghandler
import jukebox.plugs as plugin
from jukebox.multitimer import GenericTimerClass, GenericMultiTimerClass


logger = logging.getLogger('jb.timers')
cfg = jukebox.cfghandler.get_handler('jukebox')


class VolumeFadeoutError(Exception):
    """Custom exception for volume fadeout errors"""
    pass


class VolumeFadeoutAction:
    """Handles the actual volume fade out actions"""
    def __init__(self, start_volume):
        self.start_volume = start_volume
        # Use 12 steps for 2 minutes = 10 seconds per step
        self.iterations = 12
        self.volume_step = start_volume / (self.iterations - 1)
        logger.debug(f"Initialized fadeout from volume {start_volume}")

    def __call__(self, iteration, *args, **kwargs):
        """Called for each timer iteration"""
        # Calculate target volume for this step
        target_volume = max(0, int(self.start_volume - (self.iterations - iteration - 1) * self.volume_step))
        logger.debug(f"Fading volume to {target_volume} (Step {self.iterations - iteration}/{self.iterations})")
        plugin.call_ignore_errors('volume', 'ctrl', 'set_volume', args=[target_volume])


class VolumeFadoutAndShutdown:
    """Timer system that gracefully fades out volume before shutdown.

    This timer manages three coordinated timers for a smooth shutdown sequence:
    1. Main shutdown timer: Runs for the full duration and triggers the final shutdown
    2. Fadeout start timer: Triggers the volume fadeout 2 minutes before shutdown
    3. Volume fadeout timer: Handles the actual volume reduction in the last 2 minutes

    Example for a 5-minute (300s) timer:
    - t=0s:   Shutdown timer starts (300s)
              Fadeout start timer starts (180s)
    - t=180s: Fadeout start timer triggers volume reduction
              Volume fadeout begins (12 steps over 120s)
    - t=300s: Shutdown timer triggers system shutdown

    The fadeout always takes 2 minutes (120s), regardless of the total timer duration.
    The minimum total duration is 2 minutes to accommodate the fadeout period.
    All timers can be cancelled together using the cancel() method.
    """

    MIN_TOTAL_DURATION = 120  # 2 minutes minimum
    FADEOUT_DURATION = 120    # Last 2 minutes for fadeout

    def __init__(self, name):
        self.name = name
        self.default_timeout = cfg.setndefault('timers', 'volume_fadeout', 'default_timeout_sec', value=600)

        self.shutdown_timer = None
        self.fadeout_start_timer = None
        self.fadeout_timer = None

        self._reset_state()

    def _reset_state(self):
        """Reset internal state variables"""
        self.start_time = None
        self.total_duration = None
        self.current_volume = None
        self.fadeout_started = False

    def _start_fadeout(self):
        """Callback for fadeout_start_timer - initiates the volume fadeout"""
        logger.info("Starting volume fadeout sequence")
        self.fadeout_started = True

        # Get current volume at start of fadeout
        self.current_volume = plugin.call('volume', 'ctrl', 'get_volume')
        if self.current_volume <= 0:
            logger.warning("Volume already at 0, waiting for shutdown")
            return

        # Start the fadeout timer
        self.fadeout_timer = GenericMultiTimerClass(
            name=f"{self.name}_fadeout",
            iterations=12,  # 12 steps over 2 minutes = 10 seconds per step
            wait_seconds_per_iteration=10,
            callee=lambda iterations: VolumeFadeoutAction(self.current_volume)
        )
        self.fadeout_timer.start()

    def _shutdown(self):
        """Callback for shutdown_timer - performs the actual shutdown"""
        logger.info("Timer complete, initiating shutdown")
        plugin.call_ignore_errors('host', 'shutdown')

    @plugin.tag
    def start(self, wait_seconds=None):
        """Start the coordinated timer system

        Args:
            wait_seconds (float): Total duration until shutdown (optional)

        Raises:
            VolumeFadeoutError: If duration too short
        """
        # Cancel any existing timers
        self.cancel()

        # Use provided duration or default
        duration = wait_seconds if wait_seconds is not None else self.default_timeout

        # Validate duration
        if duration < self.MIN_TOTAL_DURATION:
            raise VolumeFadeoutError(f"Duration must be at least {self.MIN_TOTAL_DURATION} seconds")

        self.start_time = time.time()
        self.total_duration = duration

        # Start the main shutdown timer
        self.shutdown_timer = GenericTimerClass(
            name=f"{self.name}_shutdown",
            wait_seconds=duration,
            function=self._shutdown
        )

        # Start the fadeout start timer
        fadeout_start_time = duration - self.FADEOUT_DURATION
        self.fadeout_start_timer = GenericTimerClass(
            name=f"{self.name}_fadeout_start",
            wait_seconds=fadeout_start_time,
            function=self._start_fadeout
        )

        logger.info(
            f"Starting timer system: {fadeout_start_time}s until fadeout starts, "
            f"total duration {duration}s"
        )

        self.shutdown_timer.start()
        self.fadeout_start_timer.start()

    @plugin.tag
    def cancel(self):
        """Cancel all active timers"""
        if self.shutdown_timer and self.shutdown_timer.is_alive():
            logger.info("Cancelling shutdown timer")
            self.shutdown_timer.cancel()

        if self.fadeout_start_timer and self.fadeout_start_timer.is_alive():
            logger.info("Cancelling fadeout start timer")
            self.fadeout_start_timer.cancel()

        if self.fadeout_timer and self.fadeout_timer.is_alive():
            logger.info("Cancelling volume fadeout")
            self.fadeout_timer.cancel()

        self._reset_state()

    @plugin.tag
    def is_alive(self):
        """Check if any timer is currently active"""
        return (
            (self.shutdown_timer and self.shutdown_timer.is_alive())
            or (self.fadeout_start_timer and self.fadeout_start_timer.is_alive())
            or (self.fadeout_timer and self.fadeout_timer.is_alive())
        )

    @plugin.tag
    def get_state(self):
        """Get the current state of the timer system"""
        if not self.is_alive() or not self.start_time:
            return {
                'enabled': False,
                'type': 'VolumeFadoutAndShutdown',
                'total_duration': None,
                'remaining_seconds': 0,
                'progress_percent': 0,
                'error': None
            }

        # Use the main shutdown timer for overall progress
        elapsed = time.time() - self.start_time
        remaining = max(0, self.total_duration - elapsed)
        progress = min(100, (elapsed / self.total_duration) * 100 if self.total_duration else 0)

        return {
            'enabled': True,
            'type': 'VolumeFadoutAndShutdown',
            'total_duration': self.total_duration,
            'remaining_seconds': remaining,
            'progress_percent': progress,
            'fadeout_started': self.fadeout_started,
            'error': None
        }

    @plugin.tag
    def get_config(self):
        """Get the current configuration"""
        return {
            'default_timeout': self.default_timeout,
            'min_duration': self.MIN_TOTAL_DURATION,
            'fadeout_duration': self.FADEOUT_DURATION
        }
