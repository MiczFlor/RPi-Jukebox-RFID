import zmq
import json
import logging
import jukebox.cfghandler

cfg = jukebox.cfghandler.get_handler('jukebox')


class RpcClient:
    def __init__(self, address, context=None, *,
                 default_ignore_response=False, default_ignore_errors=False,
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
        self.queue.connect(address)

    def enqueue(self, request, ignore_response=None, ignore_errors=None):
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
            self.logger.error(f"While waiting for server response: {e}")
            if ignore_errors is False:
                raise e
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
