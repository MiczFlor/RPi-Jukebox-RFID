# -*- coding: utf-8 -*-
"""
## Remote Procedure Call Server (RPC)

Bind to tcp and/or websocket port and translates incoming requests to procedure calls.
Avaiable procedures to call are all functions registered with the plugin package.

The protocol is loosely based on [jsonrpc](https://www.jsonrpc.org/specification)

But with different elements directly relating to the plugin concept and Python function argument options

    {
      'package'  : str  # The plugin package loaded from python module
      'plugin'   : str  # The plugin object to be accessed from the package
                        # (i.e. function or class instance)
      'method'   : str  # (optional) The method of the class instance
      'args'     : [ ]  # (optional) Positional arguments as list
      'kwargs'   : { }  # (optional) Keyword arguments as dictionary
      'as_thread': bool # (optional) start call in separate thread
      'id'       : Any  # (optional) Round-trip id for response (may not be None)
      'tsp'      : Any  # (optional) measure and return total processing time for
                        # the call request (may not be None)
    }

**Response**

A response will ALWAYS be send, independent of presence of 'id'. This is in difference to the
jsonrpc specification. But this is a ZeroMQB REQ/REP pattern requirement!

If 'id' is omitted, the response will be 'None'! Unless an error occurred, then the error is returned.
The absence of 'id' indicates that the requester is not interested in the response.
If present, 'id' and 'tsp' may not be None. If they are None, there are treated as if non-existing.

**Sockets**

Three sockets are opened

1. TCP (on a configurable port)
2. Websocket (on a configurable port)
3. Inproc: On ``inproc://JukeBoxRpcServer`` connection from the internal app are accepted. This is indented be
   call arbitrary RPC functions from plugins that provide an interface to the outside world (e.g. GPIO). By also going though
   the RPC instead of calling function directly we increase thread-safety and provide easy configurability (e.g. which
   button triggers what action)

"""


import time
import zmq
import json
import logging
import jukebox.cfghandler
import jukebox.plugs as plugs

logger = logging.getLogger('jb.rpc.server')
cfg = jukebox.cfghandler.get_handler('jukebox')


class RpcServer:
    """The RPC Server Class"""
    def __init__(self, context=None):
        """Initialize the connections and bind to the ports"""
        # Get the global context (will be created if non-existing)
        logger.info(f"Init RPC Server (Pyzmq version: {zmq.pyzmq_version()}; "
                    f"ZMQ version: {zmq.zmq_version()}; has draft API: {zmq.DRAFT_API})")
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
        # This does not really exit the server
        # as the run has a blocking call to socket.recv()
        logger.info("Closing RPC Server")
        self._keep_running = False

    def run(self):
        """The main endless loop waiting for requests and forwarding the
        call request to the plugin module"""
        self._keep_running = True
        logger.info("RPC Servers started")
        # TODO: check if connected, otherwise connect or exit?

        while self._keep_running:
            # Wait for next request from client
            message = self.socket.recv()
            nt = time.time_ns()

            client_request = json.loads(message)

            logger.debug(f"Request: {client_request}")
            error = None
            result = None

            package = client_request.pop('package', None)
            if package is not None:
                plugin = client_request.pop('plugin', None)
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
                    response['id'] = request_id
            elif request_id is not None:
                response = {'result': result, 'id': request_id}
            else:
                response = {'result': None}

            if client_request.pop('tsp', None) is not None:
                response['total_processing_time'] = (nt - int(client_request['tsp'])) / 1000000
                logger.debug("Execute: Processing time: {:2.3f} ms".format(response['total_processing_time']))

            if len(client_request) != 0:
                logger.warning(f"Ignoring unknown request keys: {client_request.keys()}")

            # Send reply back to client
            logger.debug(f"Sending response: {response}")
            self.socket.send_string(json.dumps(response))
