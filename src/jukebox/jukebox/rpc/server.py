# -*- coding: utf-8 -*-

import nanotime
import zmq
import json
import logging
import jukebox.cfghandler
import jukebox.plugs as plugs

logger = logging.getLogger('jb.rpc.server')
cfg = jukebox.cfghandler.get_handler('jukebox')


class RpcServer:
    def __init__(self, context=None):
        # Get the global context (will be created if non-existing)
        logger.info("Init RPC Server")
        self.context = context or zmq.Context.instance()
        self.socket = self.context.socket(zmq.REP)

        # Inproc
        inproc_address = 'inproc://JukeBoxRpcServer'
        self.socket.bind(inproc_address)
        logger.debug(f"Connected to address '{inproc_address}'")

        # TCP
        tcp_port = cfg.getn('rpc', 'tcp_port', default=5555)
        tcp_address = f'tcp://*:{tcp_port}'
        self.socket.bind(tcp_address)
        logger.debug(f"Connected to address '{tcp_address}'")

        # WebSocket
        websocket_port = cfg.getn('rpc', 'websocket_port', default=5556)
        websocket_address = f'ws://*:{websocket_port}'
        self.socket.bind(websocket_address)
        logger.debug(f"Connected to address '{websocket_address}'")

        # socket options
        self.socket.setsockopt(zmq.LINGER, 200)
        self._keep_running = True
        logger.info('All socket connections initialized')

    def terminate(self):
        logger.info("Closing RPC Server")
        self._keep_running = False

    def run(self):
        self._keep_running = True
        logger.info("RPC Servers started")
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
            #   'package'  : str  # The plugin package loaded from python module
            #   'plugin'   : str  # The plugin object to be accessed from the package (i.e. function or class instance)
            #   'method'   : str  # (optional) The method of the class instance
            #   'args'     : [ ]  # (optional) Positional arguments as list
            #   'kwargs'   : { }  # (optional) Keyword arguments as dictionary
            #   'as_thread': bool # (optional) start call in separate thread
            #   'id'       : Any  # (optional) Round-trip id for response (may not be None)
            #   'tsp'      : Any  # (optional) measure and return total processing time for the call request (may not be None)
            # }
            # Note the difference in response behavior
            # A response will ALWAYS be send, independent of presence of 'id'
            # This is a ZeroMQB REQ/REP pattern requirement!
            # But if 'id' is omitted, this will always be 'None'! Unless an error occurred, then the error is returned
            # The absence of 'id' indicates that the requester is not interested in the response
            # If present, 'id' and 'tsp' may not be None. If they are None, there are treated as if non-existing.
            package = client_request.pop('package', default=None)
            if package is not None:
                plugin = client_request.pop('plugin', default=None)
                if plugin is not None:
                    method = client_request.pop('method', None)
                    args = client_request.pop('args', tuple())
                    kwargs = client_request.pop('kwargs', {})
                    as_thread = client_request.pop('as_thread', False)
                    try:
                        result = plugs.call(package, plugin, method, args=args, kwargs=kwargs, as_thread=as_thread)
                    except Exception as e:
                        error = f"{e.__class__.__name__}: {e.__str__()}"
                else:
                    error = "Missing mandatory parameter 'plugin'."
            else:
                error = "Missing mandatory parameter 'package'."

            request_id = client_request.pop('id', None)
            if error is not None:
                logger.error(f"Request {client_request} got error: {error}")
                response = {'error': {'code': -1, 'message': error}}
                if request_id is not None:
                    response['id'] = client_request.get('id')
            elif request_id is not None:
                response = {'result': result, 'id': client_request.get('id')}
            else:
                response = {'result': None}

            if client_request.pop('tsp', None) is not None:
                response['total_processing_time'] = (nt - int(client_request['tsp'])) / 1000000
                logger.debug("Execute: Processing time: {:2.3f} ms".format(response['total_processing_time']))

            if len(client_request) != 0:
                logger.warning(f"Ignoring unknown request keys: {client_request.keys()}")

            #  Send reply back to client
            logger.debug(f"Sending response: {response}")
            self.socket.send_string(json.dumps(response))
