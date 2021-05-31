#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import zmq
import json


class RpcClient:
    def __init__(self):
        self.context = None

    def connect(self, addr=None, zmq_context=None):
        if zmq_context is not None:
            self.context = zmq_context
            local_addr = "inproc://JukeBoxRpcServer"
        else:
            self.context = zmq.Context()
            local_addr = "tcp://127.0.0.1:5555"

        if addr is not None:
            local_addr = addr

        self.queue = self.context.socket(zmq.REQ)
        self.queue.setsockopt(zmq.RCVTIMEO, 200)
        self.queue.setsockopt(zmq.LINGER, 200)
        self.queue.connect(local_addr)

    def enqueue(self, request):
        # TODO: check reqest

        self.queue.send_string(json.dumps(request))

        print(f"send: {request}")

        try:
            server_response = self.queue.recv()
        except Exception as e:
            print("exception while waiting for rpc-server response")
            print(f"{e}")
            server_response = None

        return server_response


myRpcClient = RpcClient()
myRpcClient.connect()

#card_assignment = {"object": "player", "method": "playlistaddplay", "params": {"folder": "path to my music folder (relative to mpd music dir)"}}
card_assignment = {"object": "player", "method": "pause", "params": {"folder": "kita1"}}

resp = myRpcClient.enqueue(card_assignment)
print(resp)
