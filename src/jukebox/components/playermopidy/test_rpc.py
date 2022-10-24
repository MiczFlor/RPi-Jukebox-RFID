import asyncio
import logging
import websockets
#import jukebox.cfghandler

from jsonrpcclient import Ok, parse_json, request_json

async def main():

    """
    def __init__(self):
        self.mopidy_host_url = cfg.getn('playermopidy', 'host_url')

    def exit(self):
        logger.debug("Exit routine of playermpd started")
        self.status_is_closing = True
        self.status_thread.cancel()
        self.mpd_client.disconnect()
        self.nvm.save_all()
        return self.status_thread.timer_thread

    async def connect(self):
        #TODO figure out async stuff
        self.mopidy_client.websockets.connect(self.mopidy_host_url)


    def decode_2nd_swipe_option(self):
        cfg_2nd_swipe_action = cfg.setndefault('playermpd', 'second_swipe_action', 'alias', value='none').lower()
        if cfg_2nd_swipe_action not in [*self.second_swipe_action_dict.keys(), 'none', 'custom']:
            logger.error(f"Config mpd.second_swipe_action must be one of "
                         f"{[*self.second_swipe_action_dict.keys(), 'none', 'custom']}. Ignore setting.")
        if cfg_2nd_swipe_action in self.second_swipe_action_dict.keys():
            self.second_swipe_action = self.second_swipe_action_dict[cfg_2nd_swipe_action]
        if cfg_2nd_swipe_action == 'custom':
            custom_action = utils.decode_rpc_call(cfg.getn('playermpd', 'second_swipe_action', default=None))
            self.second_swipe_action = functools.partial(plugs.call_ignore_errors,
                                                         custom_action['package'],
                                                         custom_action['plugin'],
                                                         custom_action['method'],
                                                         custom_action['args'],
                                                         custom_action['kwargs'])
     /*"""
    
    def _mopidy_status_poll(self):
        print("hello")

    #@plugs.tag
    

    async with websockets.connect("ws://192.168.178.42:6680/mopidy/ws") as ws:  
    
            
        req = request_json("core.playback.get_current_track")
        print(req) 

        await ws.send(req)
        result = await ws.recv()
        print(result)  

        response = parse_json(result)  

        if isinstance(response, Ok):
            print(response.result)
        else:        
            logging.error(response.message)

        
asyncio.get_event_loop().run_until_complete(main())