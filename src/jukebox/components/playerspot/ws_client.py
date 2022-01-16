import logging
import websocket
import threading
from time import sleep

import jukebox.publishing as publishing

logger = logging.getLogger('jb.SpotifyWsClient')

class SpotifyWsClient:
  def __init__(self, host: str, port = 24879):
    self.protocol = 'ws'
    self.host = host
    self.port = port
    self.url = f'{self.protocol}://{self.host}:{self.port}/events'
    self.socket = None
    self.thread = None
    logger.debug(f'Spotify WS Client initialized')


  def connect(self):
    websocket.enableTrace(True)
    self.socket = websocket.WebSocketApp(
      self.url,
      on_close = self._on_close,
      on_error = self._on_error,
      on_message = self._on_message
    )
    self.thread = threading.Thread(target = self.socket.run_forever)
    self.thread.daemon = True
    self.thread.start()

    logger.debug(f'Websocket connection established to {self.url}')


  def close(self):
    self.socket.close()
    logger.debug('Websocket connection closed')


  def _on_message(self, socket, message):
    logger.debug(f'Websocket message received: {message}')


  def _on_close(self, socket):
    logger.debug('Connection with websocket server closed')


  def _on_error(self, socket, error):
    logger.error(f'Websocket error: {error}')
