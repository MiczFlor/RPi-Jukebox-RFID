import json
import logging
import websocket
import threading

logger = logging.getLogger("jb.SpotifyWsClient")

class SpotifyWsClient:
    def __init__(self, host: str, player_status, port: int = 24879):
        self.protocol = 'ws'
        self.host = host
        self.port = port
        self.url = f'{self.protocol}://{self.host}:{self.port}/events'

        self.player_status = player_status

        self.socket = None
        self.thread = None

        self.state_callbacks = {
            'contextChanged': self.context_changed,
            'trackChanged': self.track_changed,
            'playbackPaused': self.playback_paused,
            'playbackResumed': self.playback_resumed,
            'trackSeeked': self.track_seeked,
            'metadataAvailable': self.metadata_available,
        }

        logger.debug('Spotify WS Client initialized')

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

    def _on_message(self, socket, message):
        logger.debug(f'Message received: {message}')
        data = json.loads(message)
        event = data['event']

        callback = self.state_callbacks.get(event)
        if not callback:
            raise ValueError(event)

        callback(data)

    def _on_close(self, socket):
        logger.debug('Connection with websocket server closed')

    def _on_error(self, socket, error):
        logger.error(f'Websocket error: {error}')

    def metadata_available(self, message: dict):
        self.player_status.update(
            player = 'Spotify', # TODO: Should this be done differently?
            title = message['track']['name'],
            artist = message['track']['artist'][0]['name'],
            album = message['track']['album']['name'],
            albumartist = message['track']['album']['artist'][0]['name'],
            totalTime = message['track']['duration']
        )

    def context_changed(self, message: dict):
        # ['context-uri'] = message['uri']
        pass

    def track_changed(self, message: dict):
        # ['track-uri'] = message['uri']
        pass

    def playback_paused(self, message: dict):
        self.player_status.update(
            playing = False,
            timeElapsed = message['trackTime']
        )

    def playback_resumed(self, message: dict):
        self.player_status.update(
            playing = True,
            timeElapsed = message['trackTime']
        )

    def track_seeked(self, message: dict):
        self.player_status.update(
            timeElapsed = message['trackTime']
        )

