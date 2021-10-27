import zmq
import json
import logging
from typing import (List, Dict, Optional)
import jukebox.cfghandler

cfg = jukebox.cfghandler.get_handler('jukebox')


class RpcClient:
    def __init__(self, address, context=None, *,
                 default_ignore_response: bool = False, default_ignore_errors: bool = False,
                 logger=None):
        self.logger = logger
        if logger is None:
            self.logger = logging.getLogger('jb.rpc.client')
        # Get the global context (will be created if non-existing)
        self.context = context or zmq.Context.instance()
        self.queue = self.context.socket(zmq.REQ)
        self.queue.setsockopt(zmq.RCVTIMEO, 200)
        self.queue.setsockopt(zmq.LINGER, 200)
        # Default values for enqueue behaviour
        self.default_ignore_errors = default_ignore_errors
        self.default_ignore_response = default_ignore_response
        self._address = address
        self.queue.connect(address)
        self.logger.debug(f"RPC Client initialized on '{address}' (Pyzmq version: {zmq.pyzmq_version()}; "
                          f"ZMQ version: {zmq.zmq_version()}; has draft API: {zmq.DRAFT_API})")

    @property
    def address(self):
        return self._address

    def enque_raw(self, request, ignore_response: Optional[bool] = None, ignore_errors: Optional[bool] = None):
        if ignore_response is None:
            ignore_response = self.default_ignore_response
        if ignore_errors is None:
            ignore_errors = self.default_ignore_errors

        if ignore_response is False and 'id' not in request:
            request['id'] = True

        self.logger.debug(f"Send: {request}")
        self.queue.send_string(json.dumps(request))

        try:
            server_response = json.loads(self.queue.recv())
        except Exception as e:
            if ignore_errors is False:
                raise e
            self.logger.error(f"While waiting for server response: {e}")
            return None
        if 'error' in server_response:
            if ignore_errors is False:
                raise Exception(server_response['error'].get('message', 'No error message provided'))
            self.logger.debug("Ignored response error: "
                              f"{server_response['error'].get('message', 'No error message provided')}")
            return None
        if ignore_response is True:
            return None
        return server_response['result']

    def enque(self, package: str, plugin: str, method: Optional[str] = None,
              args: Optional[List] = None, kwargs: Optional[Dict] = None,
              ignore_response: Optional[bool] = None,
              ignore_errors: Optional[bool] = None):
        request = {'package': package, 'plugin': plugin}
        if method is not None:
            request['method'] = method
        if args is not None:
            request['args'] = args
        if kwargs is not None:
            request['kwargs'] = kwargs
        return self.enque_raw(request, ignore_response, ignore_errors)
