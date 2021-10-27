import threading
import jukebox.publishing.server as publishing

_THREAD_PUBLISHER = threading.local()


def get_publisher():
    """Return the publisher instance for this thread

    Per thread, only one publisher instance is required to connect to the inproc socket.
    A new instance is created if it does not already exist.

    If there is a remote-chance that your function publishing something may be called form
    different threads, always make a fresh call to ``get_publisher()`` to get the correct instance for the current thread.

    Example::

        import jukebox.publishing as publishing

        class MyClass:
            def __init__(self):
                pass

            def say_hello(name):
                publishing.get_publisher().send('hello', f'Hi {name}, howya?')

    To stress what **NOT** to do: don't get a publisher instance in the constructor and save it to ``self._pub``.
    If you do and ``say_hello`` gets called from different threads, the publisher of the thread which instantiated the class
    will be used.

    If you need your very own private Publisher Instance, you'll need to instantiate it yourself.
    But: the use cases are very rare for that. I cannot think of one at the moment.

    **Remember**: Don’t share ZeroMQ sockets between threads."""
    global _THREAD_PUBLISHER
    if not hasattr(_THREAD_PUBLISHER, 'publisher_instance'):
        _THREAD_PUBLISHER.publisher_instance = publishing.Publisher()
    return _THREAD_PUBLISHER.publisher_instance
