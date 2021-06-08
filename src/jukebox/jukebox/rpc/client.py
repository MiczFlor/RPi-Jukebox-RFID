import zmq
import json
import logging
import jukebox.cfghandler

logger = logging.getLogger('jb.rpc_client')
cfg = jukebox.cfghandler.get_handler('jukebox')


class RpcClient:
    def __init__(self, context=None):
        # Get the global context (will be created if non-existing)
        self.context = context or zmq.Context.instance()

    def connect(self, address):
        # if zmq_context is not None:
        #     self.context = zmq_context
        #     local_addr = "inproc://JukeBoxRpcServer"
        # else:
        #     self.context = zmq.Context()
        #     local_addr = "tcp://127.0.0.1:5555"
        #
        # if addr is not None:
        #     local_addr = addr

        self.queue = self.context.socket(zmq.REQ)
        self.queue.setsockopt(zmq.RCVTIMEO, 200)
        self.queue.setsockopt(zmq.LINGER, 200)
        self.queue.connect(address)

    def enqueue(self, request):
        # TODO: check reqest

        self.queue.send_string(json.dumps(request))

        logger.debug(f"send: {request}")

        try:
            server_response = self.queue.recv()
        except Exception as e:
            logger.error("exception while waiting for rpc-server response")
            logger.error(f"{e}")
            server_response = None

        return server_response


if __name__ == "__main__":
    import time
    test_objects = [{'object': 'volume', 'method': 'get', 'params': None},
                  {'object': 'volume', 'method': 'set', 'params': {'volume': 30}},
                  {'object': 'volume', 'method': 'set', 'params': {'volume': 33}},
                  {'object': 'volume', 'method': 'set', 'params': {'volume': 36}}]

    print("Test Jukebox Object Acces Client")
    rpc = RpcClient()
    print("connect")
    rpc.connect()

    print("test")
    for req in test_objects:
        # print (req)
        resp = rpc.enqueue(req)
        print(resp)
        time.sleep(0.5)
