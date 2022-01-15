import asyncio
import logging
import nest_asyncio
import websockets

import jukebox.publishing as publishing

logger = logging.getLogger('jb.SpotifyWsClient')


# Patch asyncio to make its event loop reentrant.
nest_asyncio.apply()
loop = asyncio.get_event_loop()


class SpotifyWsClient:
  def __init__(self, host: str, port = 24879):
    self.protocol = 'ws'
    self.host = host
    self.port = port
    self.authority = f'{self.protocol}://{self.host}:{self.port}'
    self.socket = None
    logger.debug(f'Spotify WS Client initialized')


  def connect(self):
    self.socket = asyncio.run_coroutine_threadsafe(self._connect_to_socket(), loop)
    tasks = [ asyncio.ensure_future(self._receive_message()) ]
    loop.run_until_complete(asyncio.wait(tasks))
    logger.debug(f'Connected to {self.authority}')


  async def _connect_to_socket(self):
    """
      Connecting to Spotify web socket
    """
    try:
      connection = await websockets.connect(self.authority)
      if connection.open:
        logger.debug(f'Web Socket connection established to {self.authority}')
        return self.connection
    except Exception as error:
        logger.error(f'Could not establish websocket connection: {error}')


  async def _receive_message(self):
      """
        Receiving all server messages and handling them
      """
      while True:
        try:
          message = await self.socket.result()
          publishing.get_publisher().send('spotify.events', message)
          logger.debug(f'Received message from server: {message}')

        except websockets.ConnectionClosed:
          logger.debug('Connection with websocket server closed')
          break
