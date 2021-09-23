import threading
import jukebox.publishing.server as publishing

_THREAD_PUBLISHER = threading.local()


def get_publisher():
    """Return the publisher instance for this thread

    Per thread, only one publisher instance is required to connect to the inproc socket.
    A new instance is created if it does not already exist

    If you need your very own private Publisher Instance, you'll need to instantiate it yourself.
    But: the use cases are very rare for that. I cannot think of one at the moment.

    Remember: Don’t share ZeroMQ sockets between threads."""
    global _THREAD_PUBLISHER
    if not hasattr(_THREAD_PUBLISHER, 'publisher_instance'):
        _THREAD_PUBLISHER.publisher_instance = publishing.Publisher()
    return _THREAD_PUBLISHER.publisher_instance
