import logging
import zmq
import json
from typing import (Optional, Iterable)

logger = logging.getLogger('jb.pub.subscriber')


class Subscriber:
    def __init__(self, url: str, topics: Optional[Iterable[str]] = None):
        self.ctx = zmq.Context.instance()
        self.socket = self.ctx.socket(zmq.SUB)
        if url is None:
            url = "tcp://localhost:5557"
        logger.debug(f"Subscriber started on '{url}'")
        self.socket.connect(url)
        if topics is None:
            self.socket.setsockopt_string(zmq.SUBSCRIBE, '')
        elif isinstance(topics, str):
            self.socket.setsockopt_string(zmq.SUBSCRIBE, topics)
        else:
            for t in topics:
                self.socket.setsockopt_string(zmq.SUBSCRIBE, t)

        logger.debug(f"ZMQ Subscriber initialized on '{url}' (Pyzmq version: {zmq.pyzmq_version()}; "
                     f"ZMQ version: {zmq.zmq_version()}; has draft API: {zmq.DRAFT_API})")

    def receive(self):
        [topic, message] = self.socket.recv_multipart()
        if message == b'':
            logger.debug(f"Revocation request for topic: {topic}")
            return [topic.decode('utf-8'), '']
        return [topic.decode('utf-8'), json.loads(message.decode('utf-8'))]
