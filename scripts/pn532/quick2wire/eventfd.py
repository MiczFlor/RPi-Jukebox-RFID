
from ctypes import *
import quick2wire.syscall as syscall
import os
import errno

# From sys/eventfd.h

EFD_SEMAPHORE = 1
EFD_CLOEXEC = 0o2000000
EFD_NONBLOCK = 0o4000

_libc = CDLL(None, use_errno=True)

eventfd_t = c_uint64

eventfd = syscall.lookup(c_int, "eventfd", (c_uint, c_int))


class Semaphore(syscall.SelfClosing):
    """A Semaphore implemented with eventfd that can be added to a Selector."""
    
    def __init__(self, count=0, blocking=True):
        """Creates a Semaphore with an initial count.
        
        Arguments:
        count -- the initial count.
        blocking -- if False calls to wait() do not block if the Semaphore
                    has a count of zero. (default = True)
        """
        self._fd = eventfd(count, EFD_SEMAPHORE|((not blocking)*EFD_NONBLOCK))
        
    def close(self):
        """Closes the Semaphore and releases its file descriptor."""
        os.close(self._fd)
    
    def fileno(self):
        """Returns the Semaphore's file descriptor."""
        return self._fd
    
    def signal(self):
        """Signal the semaphore.
        
        Signalling a semaphore increments its count by one and wakes a
        blocked task that is waiting on the semaphore.
        """
        return os.write(self._fd, eventfd_t(1))
    
    def wait(self):
        """Receive a signal from the Semaphore, decrementing its count by one.
        
        If the Semaphore is already has a count of zero, either wait
        for a signal if the Semaphore is in blocking mode, or return
        False immediately.
        
        Returns:
        True  -- the Semaphore received a signal.
        False -- the Semaphore did not receive a signal and is in 
                 non-blocking mode.
        """
        try:
            os.read(self._fd, 8)
            return True
        except OSError as e:
            if e.errno == errno.EAGAIN:
                return False
            else:
                raise
