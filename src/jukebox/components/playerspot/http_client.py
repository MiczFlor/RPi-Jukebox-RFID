import logging
import requests
from requests.adapters import HTTPAdapter
import urllib
from urllib3.util.retry import Retry

logger = logging.getLogger('jb.SpotifyHttpClient')

class SpotifyHttpClient:
  def __init__(self, host: str, port = 24879):
    self.protocol = 'http'
    self.host = host
    self.port = port
    self.authority = f'{self.protocol}://{self.host}:{self.port}'

    self.session = requests.Session()
    retries = Retry(
      total = 5,
      backoff_factor = 5,
      status_forcelist = [500, 502, 503, 504]
    )

    self.session.mount(
      self.protocol + '://',
      HTTPAdapter(max_retries = retries)
    )
    self.session.headers.update({'content-type': 'application/json'})
    logger.debug(f'Spotify HTTP Client initialized. Will connect to {self.authority}')


  def close(self):
    logger.debug("Exiting Spotify HTTP session")
    self._post_request('/instance/close')


  def _request(self, request_func, path: str):
    try:
      url = urllib.parse.urljoin(self.authority, path)
      logger.debug(f'Requesting "{self.authority}"')

      response = request_func(url)
      response.raise_for_status()

    except requests.HTTPError as http_error:
      response = {}
      logger.error(f'HTTPError: {http_error}')

    except Exception as error:
      response = {}
      logger.error(f'Error {error}')

    return response


  def _get_request(self, path: str):
    response = self._request(self.session.get, path)
    return response


  def _post_request(self, path: str):
    response = self._request(self.session.post, path)
    return response


  def play_uri(self, uri: str, play: bool = True):
    json = self._post_request(f'/player/load?uri={uri}&play={play}')
    return json


  def play(self):
    json = self._post_request('/player/resume')
    return json


  def pause(self):
    json = self._post_request('/player/pause')
    return json


  def prev(self):
    json = self._post_request('/player/prev')
    return json


  def next(self):
    json = self._post_request('/player/next')
    return json


  def seek(self, new_time: int):
    json = self._post_request(f'/player/seek?pos={new_time}')
    return json


  def shuffle(self, val: bool):
    json = self._post_request(f'/player/shuffle?val={1 if val else 0}')
    return json


  def repeatmode(self, mode: str):
    if mode == 'repeat':
        repeat_state = 'context'
    elif mode == 'single':
        repeat_state = 'track'
    else:
        repeat_state = 'none'

    json = self._post_request(f'/player/repeat?val={repeat_state}')
    return json
