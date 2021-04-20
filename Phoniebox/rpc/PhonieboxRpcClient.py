import zmq
import json

class PhonieboxRpcClient:
    
    def __init__(self):
        #self.objects = objects
        self.context = None
        
    def connect(self,addr= None):
        if addr == None:
            addr = "tcp://127.0.0.1:5555"
        self.context = zmq.Context()
        self.queue = self.context.socket(zmq.REQ)
        self.queue.setsockopt(zmq.RCVTIMEO,200)
        self.queue.setsockopt(zmq.LINGER, 200)
        self.queue.connect(addr)

    def enqueue(self, request):
        #todo check reqest 
        print (request)
        self.queue.send_string(json.dumps(request))
        
        print ("send:", request)

        try:
            server_response = self.queue.recv()
        except:
            print ("somethng went wrong")
            server_response = None
        
        return server_response


if __name__ == "__main__":
    import time
    test_objects = [{'object':'volume','method':'get','params':None},
                  {'object':'volume','method':'set','params':{'volume':30}}, 
                  {'object':'volume','method':'set','params':{'volume':33}}, 
                  {'object':'volume','method':'set','params':{'volume':36}}] 
    
    print ("Test Phonibox Object Acces Client")
    queue = phoniebox_object_access_queue()
    print ("connect")
    queue.connect()

    print ("test")
    for req  in test_objects:
        #print (req)
        resp = queue.phonie_enqueue(req)
        print (resp)
        time.sleep(0.5)
        

