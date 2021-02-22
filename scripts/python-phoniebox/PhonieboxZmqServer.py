#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import nanotime
import zmq
import json
import time

class phoniebox_control:
    
    def __init__(self,objects):
        self.objects = objects
        self.context = None
        self._keep_running = True
        
    def connect(self,addr= None):
        if addr == None:
            addr = "tcp://127.0.0.1:5555"
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.REP)
        self.socket.bind(addr)
        self.socket.setsockopt(zmq.LINGER, 200)

    def execute(self, obj, cmd, param):
        run_obj = self.objects.get(obj)
      
        if (run_obj is not None):
            run_func = getattr(run_obj,cmd,None)
            if (run_func is not None): # is callable() ??
                resp = run_func(param)
                print (resp)
            else:
                resp = {'resp': "no valid commad"}
                print (resp)
        else:
            resp = {'resp': "no valid obj"}
            print (resp)
        return resp

    def terminate(self):
        self._keep_running = False:

    def process_queue(self):
        self._keep_running = True
        while self._keep_running:
            #  Wait for next request from client
            message = self.socket.recv()
            nt = nanotime.now().nanoseconds()

            client_request=json.loads(message)
            client_response = {}

            print (client_request)

            #lets make it jsonrpc https://www.jsonrpc.org/specification
            #{"jsonrpc": "2.0", "method": "subtract", "params": {"subtrahend": 23, "minuend": 42}, "id": 3}
            #{"jsonrpc": "2.0", "result": 19, "id": 3}

            #hm, overhead, + strucure, we should takeover id 

            #{'object':'','method':'','params':{}}

            client_object = client_request.get('obj')  #lets call it object
            if (client_object != None):
                client_command = client_request.get('cmd')  #lets call it method
                client_id = client_request.get('id')
                if (client_command != None):
                    client_param = client_request.get('param') #lets call it params
                    client_response['resp'] = self.execute(client_object,client_command,client_param)
                    client_response['id'] = client_id

            client_tsp = client_request.get('tsp')
            if (client_tsp != None):
                client_response['total_processing_time'] = (nt - int(client_request['tsp'])) / 1000000
                print ("processing time: {:2.3f} ms".format(client_response['total_processing_time']))

            print(client_response)
            #  Send reply back to client
            self.socket.send_string(json.dumps(client_response))

        return (1)