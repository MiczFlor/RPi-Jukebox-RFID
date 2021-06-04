#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import zmq
import json
import logging
import time
import jukebox.cfghandler

logger = logging.getLogger('jb.pubsub_server')
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

    def publish(self, topic, payload = {}):
        self.socket.send_string("%s %s" % (topic, json.dumps(payload)))
        logger.debug("%s %s" % (topic, payload))

    def pulse(self):
        while True:
            self.publish("ping", json.dumps({ 'topic': 'ping' }))
            time.sleep(5)
