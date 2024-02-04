"""
## Publishing Server

The common publishing server for the entire Jukebox using ZeroMQ

### Structure

    +-----------------------+
    |  functional interface |   Publisher
    |                       |     - functional interface for single Thread
    |        PUB            |     - sends data to publisher (and thus across threads)
    +-----------------------+
              | (1)
              v
    +-----------------------+
    |        SUB (bind)     |   PublishServer
    |                       |     - Last Value (LV) Cache
    |        XPUB (bind)    |     - Subscriber notification and LV resend
    +-----------------------+     - independent thread
              | (2)
              v

#### Connection (1): Internal connection

Internal connection only - do not use (no, not even inside this App for you own plugins - always bind to the PublishServer)

    Protocol: Multi-part message

    Part 1: Topic (in topic tree format)
        E.g. player.status.elapsed

    Part 2: Payload or Message in json serialization
        If empty (i.e. ``b''``), it means delete the topic sub-tree from cache. And instruct subscribers to do the same

    Part 3: Command
        Usually empty, i.e. ``b''``. If not empty the message is treated as command for the PublishServer
        and the message is not forwarded to the outside. This third part of the message is never forwarded

#### Connection (2): External connection

Upon connection of a new subscriber, the entire current state is resend from cache to ALL subscribers!
Subscribers must subscribe to topics. Topics are treated as topic trees! Subscribing to a root tree will
also get you all the branch topics. To get everything, subscribe to ``b''``

    Protocol: Multi-part message

    Part 1: Topic (in topic tree format)
        E.g. player.status.elapsed

    Part 2: Payload or Message in json serialization
        If empty (i.e. b''), it means the subscriber must delete this key locally (not valid anymore)

### Why? Why?

Check out the [ZeroMQ Documentation](https://zguide.zeromq.org/docs/chapter5)
for why you need a proxy in a good design.

For use case, we made a few simplifications

### Design Rationales

* "If you need [millions of messages per second](https://zguide.zeromq.org/docs/chapter5/#Pros-and-Cons-of-Pub-Sub)
  sent to thousands of points,
  you'll appreciate pub-sub a lot more than if you need a few messages a second sent to a handful of recipients."
* "lower-volume network with a few dozen subscribers and a limited number of topics, we can use TCP and then
  the [XSUB and XPUB](https://zguide.zeromq.org/docs/chapter5/#Last-Value-Caching)"
* "Let's imagine [our feed has an average of 100,000 100-byte messages a
  second](https://zguide.zeromq.org/docs/chapter5/#High-Speed-Subscribers-Black-Box-Pattern) [...].
  While 100K messages a second is easy for a ZeroMQ application, ..."

**But we have:**

* few dozen subscribers             --> Check!
* limited number of topics          --> Check!
* max ~10 messages per second       --> Check!
* small common state information    --> Check!
* only the server updates the state --> Check!

This means, we can use less complex patters than used for these high-speed, high code count, high data rate networks :-)

* XPUB / XSUB to detect new subscriber
* Cache the entire state in the publisher
* Re-send the entire state on-demand (and then even to every subscriber)
* Using the same channel: sends state to every subscriber

**Reliability considerations**

* Late joining client (or drop-off and re-join): get full state update
* Server crash etc: No special handling necessary, we are simple
  and don't need recovery in this case. Server will publish initial state
  after re-start
* Subscriber too slow: Subscribers problem (TODO: Do we need to do anything about it?)

**Start-up sequence:**

* Publisher plugin is first plugin to be loaded
* Due to Publisher - PublisherServer structure no further sequencing required

### Plugin interactions and usage

RPC can trigger through function call in components/publishing plugin that

* entire state is re-published  (from the cache)
* a specific topic tree is re-published (from the cache)

Plugins publishing state information should publish initial state at @plugin.finalize

> [!IMPORTANT]
> Do not direclty instantiate the Publisher in your plugin module. Only one Publisher is
> required per thread. But the publisher instance **must** be thread-local!
> Always go through :func:`publishing.get_publisher()`.

**Sockets**

Three sockets are opened:

1. TCP (on a configurable port)
2. Websocket (on a configurable port)
3. Inproc: On ``inproc://PublisherToProxy`` all topics are published app-internally. This can be used for plugin modules
   that want to know about the current state on event based updates.

**Further ZeroMQ References:**

* [Working with Messages](https://zguide.zeromq.org/docs/chapter2/#Working-with-Messages)
* [Multiple Threads](https://zguide.zeromq.org/docs/chapter2/#Multithreading-with-ZeroMQ)
"""

# Developer's notes:
#
# For an explanation why you only need a single bind() for all future connect() requests,
# see the following two links:
# [https://zeromq.org/socket-api/#bind-vs-connect]
# [https://stackoverflow.com/questions/50753588/zeromq-with-norm-address-already-in-use-error-was-thrown-on-2nd-bind-why]
#
# How to integrate MQTT:
#   Create a transport bridge similar to [https://zguide.zeromq.org/docs/chapter2/#Transport-Bridging]
#   which connects to the XPUB of the PublishServer
#
# Options for later (if needed)
#   - Sequence number for clients to know they missed nothing (but we know that anyway because of 0MQ connection...)
#     Maybe for the suicidal snail pattern ?
#   - Time to live (for auto-expiring topics)

import threading
import json
import logging
import time

import zmq
from zmq.eventloop.ioloop import IOLoop
from zmq.eventloop.zmqstream import ZMQStream
from typing import (Optional)

logger = logging.getLogger('jb.pub.server')

# If tornado does not find a root logger or a logger 'tornado' WITH handler when calling IOLoop.start()
# it will just call logging.basicConfig and overwrite the current configuration!
# anaconda3/envs/rpi/lib/python3.7/site-packages/tornado/ioloop.py: _setup_logging
# So we must ensure that a logger for tornado is defined in logger.yaml -> Done!


class LastValueCache:
    def __init__(self, frontend, backend):
        self.cache = {}
        self.frontend = frontend
        self.backend = backend

    def update(self, topic, payload):
        if payload == b'':
            del self.cache[topic]
        else:
            self.cache[topic] = payload

    def send(self, topic):
        # Send out all topic(s) belonging to topic tree
        for t in self.cache.keys():
            if t.startswith(topic):
                # print(f"Sending cached topic {t}: {self.cache[t]}")
                self.backend.send_multipart([t, self.cache[t]])


class PublishServer(threading.Thread):
    """
    The publish proxy server that collects and caches messages from all internal publishers and
    forwards them to the outside world

    Handles new subscriptions by sending out the entire cached state to **all** subscribers

    The code is structures using a [Reactor Pattern](https://zguide.zeromq.org/docs/chapter5/#Using-a-Reactor)
    """
    def __init__(self, tcp_port, websocket_port):
        super().__init__(name='PubServer')
        self.daemon = True
        self.ctx = zmq.Context.instance()
        self.frontend = self.ctx.socket(zmq.SUB)
        self.frontend.bind("inproc://PublisherToProxyInternal")
        self.frontend.setsockopt(zmq.SUBSCRIBE, b'')
        self.backend = self.ctx.socket(zmq.XPUB)
        # Make sure to get notified about duplicate subscriptions
        self.backend.setsockopt(zmq.XPUB_VERBOSE, 1)

        self.backend.bind("inproc://PublisherToProxy")
        if tcp_port:
            self.backend.bind(f"tcp://*:{tcp_port}")

        if websocket_port:
            self.backend.bind(f'ws://*:{websocket_port}')

        if not tcp_port and not websocket_port:
            logger.error("Both ports disabled. Need to configure at least one port TCP or Websocket")

        # This gives a a deprecation warning if used without tornado installed
        # pip install tornado solves the issue
        self.loop = IOLoop.instance()
        # Using tornado event loop directly also works
        # self.loop = tornado.ioloop.IOLoop.instance()
        self.cache = LastValueCache(self.frontend, self.backend)
        # Wrap sockets in ZMQStreams for IOLoop handlers
        self.frontend = ZMQStream(self.frontend)
        self.backend = ZMQStream(self.backend)
        # Register our handlers with reactor
        self.frontend.on_recv(self.handle_message)
        self.backend.on_recv(self.handle_subscription)
        # Ready to go
        logger.debug(f"PublishServer initialized (Pyzmq version: {zmq.pyzmq_version()}; "
                     f"ZMQ version: {zmq.zmq_version()}; has draft API: {zmq.DRAFT_API})")

    def run(self):
        """Thread's activity"""
        self.loop.start()

    def handle_message(self, msg):
        """Handle incoming messages"""
        # logger.debug("Proxy: Receive message")
        [topic, message, cmd] = msg
        if cmd == b'':
            self.cache.update(topic, message)
            self.backend.send_multipart([topic, message])
        else:
            # It's a command: decode and execute
            if cmd == b'resend':
                self.cache.send(topic)
            elif cmd == b'close_server':
                logger.info("Closing down publish server")
                # We don't send a going-down message here. That is up to the caller before issuing the cmd!
                self.loop.stop()
                return
            else:
                logger.warning(f"Ignoring unknown server command: {cmd}")

    def handle_subscription(self, msg):
        """Handle new subscribers"""
        # msg is a 1-element list as a result of recv_multipart
        event = msg[0]
        # Event is
        # - one byte (0 = unsub / 1 = sub)
        # - followed by topic
        if event[0] == 1:
            topic = event[1:]
            logger.info(f"New subscription for topic {topic}")
            self.cache.send(topic)
        else:
            logger.info("Un-subscription received")


class Publisher:
    """
    The publisher that provides the functional interface to the application

    > [!NOTE]
    > * An instance must not be shared across threads!
    > * One instance per thread is enough

    """
    def __init__(self, check_thread_owner=True):
        """
        :param check_thread_owner: Check if send() is always called from the correct thread. This is debug feature
        and is intended to expose the situation before it leads to real trouble. Leave it on!
        """
        # Do not emit ANY logging messages in this constructor!
        # There is an option to stream logging messages via Publisher and if the Publisher
        # creates a message during initialization we have an endless recursion!

        thread = threading.currentThread()
        # logger.debug(f"Creating new publisher in thread {thread}")
        self._creating_thread = None if check_thread_owner is None else thread

        self.ctx = zmq.Context.instance()
        self.sender = self.ctx.socket(zmq.PUB)
        self.sender.connect("inproc://PublisherToProxyInternal")
        # There is a little sleep necessary here for everything to get up running
        # Else you may loose the first message(s)
        time.sleep(0.05)
        self._recursion = 0

    def _send(self, topic: bytes, message: bytes, cmd: bytes):
        if self._creating_thread is not None and self._creating_thread != threading.currentThread():
            # Detect the recursion which creating a log message inside send creates and suppress it
            # We want the error message to appear also on the publisher stream, so we keep it and make do with the
            # recursion detection
            if self._recursion == 0:
                self._recursion += 1
                logger.error(f"Publish command from different thread '{threading.currentThread().name}' "
                             f"than publisher was created from '{self._creating_thread.name}'!")
            self._recursion = 0
        self.sender.send_multipart([topic, message, cmd])

    def send(self, topic: str, payload):
        """Send out a message for topic"""
        # logger.debug(f"Send topic '{topic}'")
        self._send(topic.encode('utf-8'), json.dumps(payload).encode('utf-8'), b'')

    def revoke(self, topic: str):
        """Revoke a single topic element (not a topic tree!)"""
        # logger.debug(f"Revoke topic '{topic}'")
        self._send(topic.encode('utf-8'), b'', b'')

    # ----------------------------------------------------------------
    # The following are commands to the PublishServer
    # ----------------------------------------------------------------

    def resend(self, topic: Optional[str] = None):
        """Instructs the PublishServer to resend current status to all subscribers

        Not necessary to call after incremental updates or new subscriptions - that will happen automatically!"""
        logger.debug("Sending command 'resend' to PublishServer")
        if topic is None:
            topic = ''
        self._send(topic.encode('utf-8'), b'', 'resend'.encode('utf-8'))

    def close_server(self):
        """Instructs the PublishServer to close itself down"""
        logger.debug("Sending command 'close' to PublishServer")
        self._send(b'', b'', 'close_server'.encode('utf-8'))
