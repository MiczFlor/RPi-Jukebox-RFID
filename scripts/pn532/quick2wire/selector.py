"""Event notification for I/O, timers, inter-thread and inter-process
communication.
"""

import select
from quick2wire.syscall import SelfClosing
from quick2wire.eventfd import Semaphore
from quick2wire.timerfd import Timer

INPUT = select.EPOLLIN
OUTPUT = select.EPOLLOUT
ERROR = select.EPOLLERR
HANGUP = select.EPOLLHUP
PRIORITY_INPUT = select.EPOLLPRI

LEVEL = 0
EDGE = 1


class Selector(SelfClosing):
    """Lets a thread wait for multiple events and handle them one at a time."""
    
    def __init__(self, size_hint=-1):
        """Initialises a Selector.
        
        Arguments:
        size_hint -- A hint of the number of event sources that will
                     be added to the Selector, or -1 for the default.
                     Used to optimize internal data structures, it
                     doesn't limit the maximum number of monitored
                     event sources.
        """
        self._epoll = select.epoll(size_hint)
        self._sources = {}
        self.ready = None
        self.events = 0
        
    def fileno(self):
        """Returns the Selector's file descriptor."""
        return self._epoll.fileno()
    
    def add(self, source, eventmask=INPUT|ERROR, trigger=None, identifier=None):
        """Adds an event source to the Selector.
        
        Arguments:
        source     -- the event source to add.  Must provide a fileno() 
                      method that returns its file descriptor.
                      
        eventmask  -- the events that the Selector will report.  A
                      bit-mask of:
                      INPUT          -- there is input to be read from 
                                        the source
                      OUTPUT         -- output can be written to the source
                      ERROR          -- an error has occurred on the source
                      HANGUP         -- a remote hangup has occured on the 
                                        source
                      PRIORITY_INPUT -- urgent out-of-band data is waiting 
                                        to be read from the source
                      The default is INPUT|ERROR.
        trigger    -- LEVEL -- the event source is level triggered (the 
                      default),
                      EDGE  -- the event source is edge triggered.
        identifier -- A value to be stored in the `ready` property when an
                      event has occurred on the source.  Default is the 
                      source itself.
        """
        fileno = source.fileno()
        trigger = trigger if trigger is not None else getattr(source, "__trigger__", LEVEL)
        
        self._sources[fileno] = identifier if identifier is not None else source
        self._epoll.register(fileno, eventmask|(select.EPOLLET*trigger))
    
    def remove(self, source):
        """Removes an event source from the Selector.
        
        Arguments:
        source -- the event source to remove.
        """
        fileno = source.fileno()
        self._epoll.unregister(source)
        del self._sources[fileno]

    def wait(self, timeout=-1):
        """Wait for an event to occur on any of the sources that have been added to the Selector.
        
        After wait returns, the `ready` property is set to the
        identifier of a source that has an event that needs to be
        responded to and the `events` property is set to a bit-set
        indicating which events have occurred on the source.  The
        `has_input`, `has_output`, `has_error`, `has_hangup` and
        `has_priority_input` events provide convenient access to the
        bits of the `event` bit-set.
        
        If a timeout is specified and no events occur before the
        timeout, the `ready` property is `None`.
        
        Arguments: 
        timeout -- maximum time to wait for an event. Specified in
                   seconds (can be less than one). Default is no
                   timeout: wait forever for an event.
        """
        self.ready = None
        self.events = 0
        
        readies = self._epoll.poll(timeout, maxevents=1)
        if readies:
            fileno, self.events = readies[0]
            self.ready = self._sources[fileno]
            
    @property
    def has_input(self):
        """Returns whether the ready event source has input that can be read."""
        return bool(self.events & INPUT)
    
    @property
    def has_output(self):
        """Returns whether output can be written to the ready event source."""
        return bool(self.events & OUTPUT)
    
    @property
    def has_error(self):
        """Returns whetheran error has occurred on the ready event source."""
        return bool(self.events & ERROR)
    
    @property
    def has_hangup(self):
        """Returns whether a remote hangup has occured on the ready event source."""
        return bool(self.events & HANGUP)
    
    @property
    def has_priority_input(self):
        """Returns whether urgent out-of-band data is waiting to be read from the ready event source."""
        return bool(self.events & PRIORITY_INPUT)
    
    def close(self):
        """Closes the Selector and releases its file descriptor."""
        self._epoll.close()

__all__ = ['Selector', 'Timer', 'Semaphore', 'INPUT', 'OUTPUT', 'ERROR', 'HANGUP', 'PRIORITY_INPUT', 'LEVEL', 'EDGE']
