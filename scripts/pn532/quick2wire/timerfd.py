

import math
import os
from ctypes import *
import struct
from contextlib import closing
import quick2wire.syscall as syscall


# From <time.h>

time_t = c_long

clockid_t = c_ulong

class timespec(Structure):
    _fields_ = [("sec", time_t),
                ("nsec", c_long)]
    
    __slots__ = [name for name,type in _fields_]
    
    @classmethod
    def from_seconds(cls, secs):
        t = cls()
        t.seconds = secs
        return t
    
    @property
    def seconds(self):
        if self.nsec == 0:
            return self.sec
        else:
            return self.sec + self.nsec / 1000000000.0
        
    @seconds.setter
    def seconds(self, secs):
        fractional, whole = math.modf(secs)
        self.sec = int(whole)
        self.nsec = int(fractional * 1000000000)


class itimerspec(Structure):
    _fields_ = [("interval", timespec), 
                ("value", timespec)]
    
    __slots__ = [name for name,type in _fields_]
    
    @classmethod
    def from_seconds(cls, offset, interval):
        spec = cls()
        spec.value.seconds = offset
        spec.interval.seconds = interval
        return spec


# from <bits/time.h>

CLOCK_REALTIME           = 0 # Identifier for system-wide realtime clock.
CLOCK_MONOTONIC	         = 1 # Monotonic system-wide clock.
CLOCK_PROCESS_CPUTIME_ID = 2 # High-resolution timer from the CPU
CLOCK_THREAD_CPUTIME_ID	 = 3 # Thread-specific CPU-time clock. 
CLOCK_MONOTONIC_RAW      = 4 # Monotonic system-wide clock, not adjusted for frequency scaling. 
CLOCK_REALTIME_COARSE    = 5 # Identifier for system-wide realtime clock, updated only on ticks. 
CLOCK_MONOTONIC_COARSE   = 6 # Monotonic system-wide clock, updated only on ticks. 
CLOCK_BOOTTIME	         = 7 # Monotonic system-wide clock that includes time spent in suspension. 
CLOCK_REALTIME_ALARM     = 8 # Like CLOCK_REALTIME but also wakes suspended system.
CLOCK_BOOTTIME_ALARM     = 9 # Like CLOCK_BOOTTIME but also wakes suspended system.


# From <sys/timerfd.h>

# Bits to be set in the FLAGS parameter of `timerfd_create'.
TFD_CLOEXEC = 0o2000000,
TFD_NONBLOCK = 0o4000

# Bits to be set in the FLAGS parameter of `timerfd_settime'.
TFD_TIMER_ABSTIME = 1 << 0



# Return file descriptor for new interval timer source.
#
# extern int timerfd_create (clockid_t __clock_id, int __flags)

timerfd_create = syscall.lookup(c_int, "timerfd_create", (clockid_t, c_int))

# Set next expiration time of interval timer source UFD to UTMR.  If
# FLAGS has the TFD_TIMER_ABSTIME flag set the timeout value is
# absolute.  Optionally return the old expiration time in OTMR.
#
# extern int timerfd_settime (int __ufd, int __flags,
# 			      __const struct itimerspec *__utmr,
# 			      struct itimerspec *__otmr)
timerfd_settime = syscall.lookup(c_int, "timerfd_settime", (c_int, c_int, POINTER(itimerspec), POINTER(itimerspec)))

# Return the next expiration time of UFD.
#
# extern int timerfd_gettime (int __ufd, struct itimerspec *__otmr)

timerfd_gettime = syscall.lookup(c_int, "timerfd_gettime", (c_int, POINTER(itimerspec)))


class Timer(syscall.SelfClosing):
    """A one-shot or repeating timer that can be added to a Selector."""
    
    def __init__(self, offset=0, interval=0, blocking=True, clock=CLOCK_REALTIME):
        """Creates a new Timer.
        
        Arguments:
        offset   -- the initial expiration time, measured in seconds from
                    the call to start().
        interval -- if non-zero, the interval for periodic timer expirations, 
                    measured in seconds.
        blocking -- if False calls to wait() do not block until the timer 
                    expires but return 0 if the timer has not expired. 
                    (default = True)
        clock    -- the system clock used to measure time:
                    CLOCK_REALTIME  -- system-wide realtime clock.
                    CLOCK_MONOTONIC -- monotonic system-wide clock.
        """
        self._fd = timerfd_create(clock, (not blocking)*TFD_NONBLOCK)
        self._offset = offset
        self._interval = interval
        self._started = False
    
    def close(self):
        """Closes the Timer and releases its file descriptor."""
        os.close(self._fd)
        self._fd = None
        
    def fileno(self):
        """Returns the Timer's file descriptor."""
        return self._fd

    @property
    def offset(self):
        """the initial expiration time, measured in seconds from the call to start()."""
        return self._offset
    
    @offset.setter
    def offset(self, new_offset):
        self._offset = new_offset
        if self._started:
            self._apply_schedule()
    
    @property
    def interval(self):
        """The interval, specified in seconds, with which the timer will repeat.
        
        If zero, the timer only fires once, when the offset expires.
        """
        return self._interval
    
    @interval.setter
    def interval(self, new_interval):
        self._interval = new_interval
        if self._started:
            self._apply_schedule()
    
    def start(self):
        """Starts the timer running.
        
        Raises:
        ValueError -- if offset and interval are both zero.
        """
        if self._offset == 0 and self._interval == 0:
            raise ValueError("timer will not fire because offset and interval are both zero")
        
        self._apply_schedule()
        self._started = True
        
    def stop(self):
        """Stops the timer running. Any scheduled timer events will not fire."""
        self._schedule(0, 0)
        self._started = False
    
    def wait(self):
        """Receives timer events.
        
        If the timer has already expired one or more times since its
        settings were last modified or wait() was last called then
        wait() returns the number of expirations that have occurred.

        If no timer expirations have occurred, then the call either
        blocks until the next timer expiration, or returns 0 if the
        Timer is non-blocking (was created with the blocking parameter
        set to False).
        
        Raises:
        OSError -- an OS error occurred reading the state of the timer.
        """
        try:
            buf = os.read(self._fd, 8)
            return struct.unpack("Q", buf)[0]
        except OSError as e:
            if e.errno == errno.EAGAIN:
                return 0
            else:
                raise e
    
    def _apply_schedule(self):
        self._schedule(self._offset or self._interval, self._interval)
    
    def _schedule(self, offset, interval):
        spec = itimerspec.from_seconds(offset, interval)
        timerfd_settime(self._fd, 0, byref(spec), None)
    
