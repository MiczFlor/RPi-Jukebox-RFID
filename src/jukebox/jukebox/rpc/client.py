import zmq
import json


class PhonieboxRpcClient:

    def __init__(self):
        self.context = None

    def connect(self, addr=None, zmq_context=None):
        if zmq_context is not None:
            self.context = zmq_context
            local_addr = "inproc://PhonieboxRpcServer"
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
        print(request)
        self.queue.send_string(json.dumps(request))

        print("send:", request)

        try:
            server_response = self.queue.recv()
        except Exception as e:
            print("somethng went wrong:")
            print(e)
            server_response = None

        return server_response


if __name__ == "__main__":
    import time
    test_objects = [{'object': 'volume', 'method': 'get', 'params': None},
                  {'object': 'volume', 'method': 'set', 'params': {'volume': 30}},
                  {'object': 'volume', 'method': 'set', 'params': {'volume': 33}},
                  {'object': 'volume', 'method': 'set', 'params': {'volume': 36}}]

    print("Test Jukebox Object Acces Client")
    rpc = PhonieboxRpcClient()
    print("connect")
    rpc.connect()

    print("test")
    for req in test_objects:
        # print (req)
        resp = rpc.enqueue(req)
        print(resp)
        time.sleep(0.5)
