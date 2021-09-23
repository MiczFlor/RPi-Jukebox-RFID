#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""

"""


import zmq
import json
import logging
import jukebox.cfghandler
import threading

logger = logging.getLogger('jb.pubsub.server')
cfg = jukebox.cfghandler.get_handler('jukebox')


class PubSubServer:
    def __init__(self, context=None):
        # Get the global context (will be created if non-existing)
        self.context = context or zmq.Context.instance()
        self.socket = self.context.socket(zmq.PUB)

        # WebSocket
        websocket_port = cfg.getn('pubsub', 'websocket_port', default=5557)
        websocket_address = f'ws://*:{websocket_port}'
        self.socket.bind(websocket_address)
        logger.debug(f"Connected to '{websocket_address}'")

        # Inproc
        inproc_address = 'inproc://JukeBoxPubServer'
        self.socket.bind(inproc_address)
        logger.debug(f"Connected to address '{inproc_address}'")

        # TCP
        tcp_port = cfg.getn('pubsub', 'tcp_port', default=5559)
        tcp_address = f'tcp://*:{tcp_port}'
        self.socket.bind(tcp_address)
        logger.debug(f"Connected to address '{tcp_address}'")

        self._lock = threading.Lock()

    def publish(self, topic, payload=None):
        with self._lock:
            if payload is None:
                payload = {}
            # self.socket.send_string("%s %s" % (topic, json.dumps(payload)))
            self.socket.send_multipart([topic.encode('utf-8'), json.dumps(payload).encode('utf-8')])
        # logger.debug("%s %s" % (topic, payload))
