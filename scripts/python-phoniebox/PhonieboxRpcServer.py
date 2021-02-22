#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import nanotime
import zmq
import json
import time

class phoniebox_rpc_server:
    
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
        call_obj = self.objects.get(obj)
      
        if (call_obj is not None):
            call_function = getattr(call_obj,cmd,None)
            if (call_function is not None): # is callable() ??
                response = call_function(param)
                print (response)
            else:
                response = {'resp': "no valid commad"}
                print (response)
        else:
            response = {'resp': "no valid obj"}
            print (response)
        return response

    def terminate(self):
        self._keep_running = False

    def server(self):
        self._keep_running = True
        #todo: check if connected, otherwise connect or exit?

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