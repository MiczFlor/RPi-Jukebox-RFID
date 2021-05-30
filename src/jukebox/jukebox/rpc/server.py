#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import nanotime
import zmq
import json
import logging
import jukebox.cfghandler

logger = logging.getLogger('jb.rpc_server')
cfg = jukebox.cfghandler.get_handler('jukebox')


class RpcServer:
    def __init__(self, objects, context=None):
        # Get the global context (will be created if non-existing)
        self.context = context or zmq.Context.instance()
        self.socket = self.context.socket(zmq.REP)

        # Inproc
        inproc_address = 'inproc://JukeBoxRpcServer'
        self.socket.bind(inproc_address)
        logger.info(f"Connected to port '{inproc_address}'")

        # TCP
        tcp_port = cfg.getn('rpc', 'tcp_port', default=5555)
        tcp_address = f'tcp://*:{tcp_port}'
        self.socket.bind(tcp_address)
        logger.info(f"Connected to port '{tcp_address}'")

        # WebSocket
        websocket_port = cfg.getn('rpc', 'websocket_port', default=5556)
        websocket_address = f'ws://*:{websocket_port}'
        self.socket.bind(websocket_address)
        logger.info(f"Connected to port '{websocket_address}'")

        ## socket options
        self.socket.setsockopt(zmq.LINGER, 200)
        self.objects = objects
        self._keep_running = True
        logger.info('All socket connections initialized')

    def terminate(self):
        self._keep_running = False

    def execute(self, module, method, args, kwargs):
        """
        Call the method in module with args and kwargs

        Arguments and keyword arguments will be unpacked when calling the function
        :param module: The plugin module
        :param method: The registers function within the plugin module
        :param args: Set with arguments passed to the function. Pass empty set if unneeded
        :param kwargs: Dict with keyword arguments. Pass an empty dict if unneeded
        :return: The return value of the method in the RPC protocol format or an error message
        """
        if module in self.objects:
            method_attr = getattr(self.objects[module], method, None)
            if callable(method_attr):
                try:
                    response = {'result': method_attr(*args, **kwargs)}
                except Exception as e:
                    response = {'error': {'code': -1, 'message': f"Error while executing method: '{method_attr}' in '{module}'. Reason: {e}"}}
            else:
                response = {'error': {'code': -1, 'message': f"Method not callable: '{method}' in '{module}'"}}
        else:
            response = {'error': {'code': -1, 'message': f"Unknown plugin object: '{module}'"}}
        return response

    def run(self):
        self._keep_running = True
        # TODO: check if connected, otherwise connect or exit?

        while self._keep_running:
            #  Wait for next request from client
            message = self.socket.recv()
            nt = nanotime.now().nanoseconds()

            client_request = json.loads(message)

            logger.debug(f"Request: {client_request}")

            # in difference to jsonrpc https://www.jsonrpc.org/specification
            # {'plugin': '', 'method':'', 'args': { //optional }, 'kwargs': { //optional }}
            module = client_request.get('plugin')
            if module is not None:
                method = client_request.get('method')
                if method is not None:
                    args = client_request.get('args', set())
                    kwargs = client_request.get('kwargs', {})
                    response = self.execute(module, method, args, kwargs)
                else:
                    response = {'error': {'code': -1, 'message': "Missing mandatory parameter 'method'."}}
            else:
                response = {'error': {'code': -1, 'message': "Missing mandatory parameter 'plugin'."}}

            if 'tsp' in client_request:
                response['total_processing_time'] = (nt - int(client_request['tsp'])) / 1000000
                logger.debug("Execute: Processing time: {:2.3f} ms".format(response['total_processing_time']))

            if 'id' in client_request:
                response['id'] = client_request.get('id')

            if 'error' in response:
                logger.error(f"Execute: {response['error']['message']}")

            logger.debug(f"Execute: {response}")

            #  Send reply back to client
            self.socket.send_string(json.dumps(response))
