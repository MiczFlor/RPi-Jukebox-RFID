#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import nanotime
import zmq
import json
import logging

logger = logging.getLogger('jb.rpc_server')


class RpcServer:

    def __init__(self, objects):
        self.objects = objects
        self.context = None
        self._keep_running = True

    def connect(self, addrs=None):
        if addrs is None:
            addrs = ["tcp://*:5555", "inproc://JukeBoxRpcServer", "ws://*:5556"]
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.REP)
        for addr in addrs:
            self.socket.bind(addr)
        self.socket.setsockopt(zmq.LINGER, 200)
        return self.context

    def execute(self, obj, cmd, param):
        call_obj = self.objects.get(obj)

        if (call_obj is not None):
            call_function = getattr(call_obj, cmd, None)
            if (call_function is not None):  # better to check with is callable() ??
                response = call_function(param)
            else:
                response = {'resp': "no valid commad"}
        else:
            response = {'resp': "no valid obj"}
        # print (response)
        return response

    def terminate(self):
        self._keep_running = False

    def run(self):
        self._keep_running = True
        # TODO: check if connected, otherwise connect or exit?

        while self._keep_running:
            #  Wait for next request from client
            message = self.socket.recv()
            nt = nanotime.now().nanoseconds()

            client_request = json.loads(message)
            client_response = {}

            logger.debug(client_request)

            # in difference to jsonrpc https://www.jsonrpc.org/specification
            # {"jsonrpc": "2.0", "method": "subtract", "params": {"subtrahend": 23, "minuend": 42}, "id": 3}
            # a additional required parameter "object" is used:
            # {'object':'','method':'','params':{},id:''}

            client_object = client_request.get('object')
            if (client_object is not None):
                client_command = client_request.get('method')
                client_id = client_request.get('id')
                if (client_command is not None):
                    client_param = client_request.get('params')
                    client_response['resp'] = self.execute(client_object, client_command, client_param)
                    client_response['id'] = client_id

            client_tsp = client_request.get('tsp')
            if (client_tsp is not None):
                client_response['total_processing_time'] = (nt - int(client_request['tsp'])) / 1000000
                logger.debug("processing time: {:2.3f} ms".format(client_response['total_processing_time']))

            logger.debug(client_response)
            #  Send reply back to client
            self.socket.send_string(json.dumps(client_response))

        return (1)
