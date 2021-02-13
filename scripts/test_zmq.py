import nanotime
import zmq
import json
import time

import alsaaudio
from mpd import MPDClient

class player_control:
    def __init__(self):
        self.mpd_client = MPDClient()               # create client object
        self.mpd_client.timeout = 0.5               # network timeout in seconds (floats allowed), default: None
        self.mpd_client.idletimeout = 0.5           # timeout for fetching the result of the idle command is handled seperately, default: None
        #self.mpd_client.connect("localhost", 6600)  # connect to localhost:6600
        self.connect()
        print("Connected to MPD Version: "+self.mpd_client.mpd_version)

    def connect(self):
        self.mpd_client.connect("localhost", 6600)  # connect to localhost:6600
    
    def get_player_type_and_version(self, param):
        return ({'tpye':'mpd','version':self.mpd_client.mpd_version})
    
    def play(self, param):
        try:
            self.mpd_client.play()
        except ConnectionError: 
            print ("MPD Connection Error, retry")
            self.conncet()
            self.mpd_client.play()
        except  Exception as e:
            print(e)
        song = self.mpd_client.currentsong()
        return ({'song':song})
        
    def get_current_song(self, param):
        song = self.mpd_client.currentsong()
        #resp = {'resp': self.mpd_client.currentsong()}
        return song

class volume_control_mpd:
    def __init__(self):
        print ("not yet implemented\n")

class volume_control_alsa:
    def __init__(self):
         self.mixer = alsaaudio.Mixer('PCM',  0)
         self.volume = 0
         #self.mixer.getvolume()

    def get(self, param):
        return ({'volume':self.volume})

    def set(self, param):
        volume = param.get('volume')
        if isinstance(volume, int):
            if (volume < 0): volume = 0;
            if (volume > 100): volume = 100;
            self.volume = volume
            self.mixer.setvolume(self.volume)
        else:
            volume = -1
        return ({'volume':volume})

    def inc(self, param):
        volume = self.volume +3
        if (volume > 100): volume = 100
        self.volume = volume
        self.mixer.setvolume(self.volume)
        return ({'volume':self.volume})

    def dec(self, param):
        volume = self.volume -3
        if (volume < 0): volume = 0
        self.volume = volume
        self.mixer.setvolume(self.volume)
        return ({'volume':self.volume})

class phoniebox_control:
    
    def __init__(self,objects):
        self.objects = objects
        self.context = None
        
    def connect(self,addr= None):
        if addr == None:
            addr = "tcp://127.0.0.1:5555"
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.REP)
        self.socket.bind(addr)
        self.socket.setsockopt(zmq.LINGER, 200)

    def run(self, obj, cmd, param):
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

    def process_queue(self):
        #while True:
        #  Wait for next request from client
        message = self.socket.recv()
        nt = nanotime.now().nanoseconds()
    
        client_request=json.loads(message)
        client_response = {}

        print (client_request)

        client_object = client_request.get('obj')
        if (client_object != None):
            client_command = client_request.get('cmd')
            if (client_command != None):
                client_param = client_request.get('param')
                client_response['resp'] = self.run(client_object,client_command,client_param)

        client_tsp = client_request.get('tsp')
        if (client_tsp != None):
            client_response['total_processing_time'] = (nt - int(client_request['tsp'])) / 1000000
            print ("processing time: {:2.3f} ms".format(client_response['total_processing_time']))
        
        print(client_response)
        #  Send reply back to client
        self.socket.send_string(json.dumps(client_response))

        return (1)


#def get(self):
#      def func_not_found(): # just in case we dont have the function
#         print 'No Function '+self.i+' Found!'
#      func_name = 'function' + self.i
#      func = getattr(self,func_name,func_not_found) 
#      func() # <-- this should work!


if __name__ == "__main__":
    #initialize objcts
    objects = {'volume':volume_control_alsa(),
               'player':player_control()}

    print ("Start Phonibox Control")
    pc = phoniebox_control(objects)
    pc.connect()

    print ("Start loop")
    ret_ok = 1
    while (ret_ok):
        ret_ok = pc.process_queue()
    