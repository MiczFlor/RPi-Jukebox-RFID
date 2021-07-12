#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import nanotime
import zmq
import json
import logging
import jukebox.cfghandler
import jukebox.plugin as plugin

logger = logging.getLogger('jb.rpc_server')
cfg = jukebox.cfghandler.get_handler('jukebox')


class RpcServer:
    def __init__(self, context=None):
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

        # socket options
        self.socket.setsockopt(zmq.LINGER, 200)
        self._keep_running = True
        logger.info('All socket connections initialized')

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

            logger.debug(f"Request: {client_request}")
            error = None
            result = None

            # Based on jsonrpc https://www.jsonrpc.org/specification
            # But with different elements
            # {
            #   'plugin'   : str # The plugin name of the loaded module,
            #   'object'   : str # The callable object (e.g. function) or class instance,
            #   'method'   : str # (optional) The method of the class instance,
            #   'args'     : [ ] # (optional) positional arguments as list,
            #   'kwargs'   : { } # (optional) keyword arguments as dictionary
            #   'as_thread': true/false # (optional) start call in separate thread
            #   'id'       : Any # (optional) Round-trip id for response
            #   'tsp'      : Any # (optional) measure and return total processing time for the call request
            # }
            # Note the difference in response behavior
            # A response will ALWAYS be send, independent of presence of 'id'
            # This is a ZeroMQB REQ/REP pattern requirement!
            # But if 'id' is omitted, this will always be None! Unless an error occured, then the error is returned
            # The absence of 'id' indicates that the requester is not interested in the response
            module = client_request.get('plugin')
            if module is not None:
                obj = client_request.get('object')
                if obj is not None:
                    method = client_request.get('method', None)
                    args = client_request.get('args', set())
                    kwargs = client_request.get('kwargs', {})
                    as_thread = client_request.get('as_thread', False)
                    try:
                        result = plugin.call(module, obj, method, args=args, kwargs=kwargs, as_thread=as_thread)
                    except Exception as e:
                        error = e.__str__()
                else:
                    error = "Missing mandatory parameter 'object'."
            else:
                error = "Missing mandatory parameter 'plugin'."

            if error is not None:
                logger.error(f"Execute error: {error} in request {client_request}")
                response = {'error': {'code': -1, 'message': error}}
                if 'id' in client_request:
                    response['id'] = client_request.get('id')
            elif 'id' in client_request:
                response = {'result': result, 'id': client_request.get('id')}
            else:
                response = {'result': None}

            if 'tsp' in client_request:
                response['total_processing_time'] = (nt - int(client_request['tsp'])) / 1000000
                logger.debug("Execute: Processing time: {:2.3f} ms".format(response['total_processing_time']))

            #  Send reply back to client
            logger.debug(f"Sending response: {response}")
            self.socket.send_string(json.dumps(response))
