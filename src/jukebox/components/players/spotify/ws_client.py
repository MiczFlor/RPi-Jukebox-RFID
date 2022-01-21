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
            'playbackPaused': self.playback_paused,
            'playbackResumed': self.playback_resumed,
            'playbackHaltStateChanged': self.playback_halted,
            'trackSeeked': self.track_seeked,
            'metadataAvailable': self.metadata_available,
            'inactiveSession': self.inactive_session,
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
        logger.debug(f'_on_message: {message}')
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


    # We only care about seconds, not ms as provided by Spotify
    def _round_time_to_seconds(self, time):
        return '{:.1f}'.format(time / 1000)

    def metadata_available(self, data: dict):
        cover_art = data['track']['album']['coverGroup']['image'][2]['fileId'].lower()

        self.player_status.update(
            player = 'Spotify', # TODO: Should this be done differently?
            trackid = data['track']['gid'],
            title = data['track']['name'],
            artist = data['track']['artist'][0]['name'],
            album = data['track']['album']['name'],
            albumartist = data['track']['album']['artist'][0]['name'],
            duration = self._round_time_to_seconds(data['track']['duration']),
            coverArt =cover_art
        )

    def playback_paused(self, data: dict):
        self.player_status.update(
            playing = False,
            elapsed = self._round_time_to_seconds(data['trackTime'])
        )

    def playback_resumed(self, data: dict):
        self.player_status.update(
            playing = True,
            elapsed = self._round_time_to_seconds(data['trackTime'])
        )

    def playback_halted(self, data: dict):
        self.player_status.update(
            playing = data['halted'],
            elapsed = self._round_time_to_seconds(data['trackTime'])
        )

    def track_seeked(self, data: dict):
        self.player_status.update(
            elapsed = self._round_time_to_seconds(data['trackTime'])
        )

    # When Spotify session is routed to another device,
    # the local session goes inactive
    def inactive_session(self, data: dict):
        self.player_status.update(playing = False)
