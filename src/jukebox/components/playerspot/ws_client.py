import json
import logging
import websocket
import threading

from jukebox import publishing

logger = logging.getLogger("jb.SpotifyWsClient")


class SpotifyWsClient:

    def __init__(self, host: str, port=24879):
        self.protocol = "ws"
        self.host = host
        self.port = port
        self.url = f"{self.protocol}://{self.host}:{self.port}/events"
        self.socket = None
        self.thread = None
        self.known_state = {"contextChanged": self.context_changed,
                            "trackChanged": self.track_changed,
                            "playbackPaused": self.playback_paused,
                            "playbackResumed": self.playback_resumed,
                            "trackSeeked": self.track_seeked,
                            "metadataAvailable": self.metadata_available,
                            }
        self.spot_status = {}
        logger.debug("Spotify WS Client initialized")

    def connect(self):
        websocket.enableTrace(True)
        self.socket = websocket.WebSocketApp(
            self.url,
            on_close=self._on_close,
            on_error=self._on_error,
            on_message=self._on_message
        )
        self.thread = threading.Thread(target=self.socket.run_forever)
        self.thread.daemon = True
        self.thread.start()

        logger.debug(f"Websocket connection established to {self.url}")

    def close(self):
        self.socket.close()
        logger.debug("Websocket connection closed")

    def _on_message(self, socket, message):
        logger.debug(f"Websocket message received: {message}")
        converted_message = json.loads(message)
        event = converted_message["event"]
        logger.debug(f"Event from Message: {event}")
        if event in self.known_state.keys():
            func = self.known_state.get(event)
            func(converted_message)
        publishing.get_publisher().send('playerspotstatus', self.spot_status)

    def _on_close(self, socket):
        logger.debug("Connection with websocket server closed")

    def _on_error(self, socket, error):
        logger.error(f"Websocket error: {error}")

    def context_changed(self, message: dict):
        logger.debug("contextChanged called")
        self.spot_status["context-uri"] = message["uri"]

    def track_changed(self, message: dict):
        logger.debug("trackChanged called")
        self.spot_status["track-uri"] = message["uri"]

    def playback_paused(self, message: dict):
        logger.debug("playbackPaused called")
        self.spot_status["state"] = "paused"
        self.spot_status["trackTime"] = message["trackTime"]

    def playback_resumed(self, message: dict):
        logger.debug("playbackResumed called")
        self.spot_status["state"] = "play"
        self.spot_status["trackTime"] = message["trackTime"]

    def track_seeked(self, message: dict):
        logger.debug("trackSeeked called")
        self.spot_status["trackTime"] = message["trackTime"]

    def metadata_available(self, message: dict):
        logger.debug("metadataAvailable called")
        self.spot_status["title"] = message["track"]["name"]
        self.spot_status["artist"] = message["track"]["artist"][0]["name"]
        self.spot_status["album"] = message["track"]["album"]["name"]
        self.spot_status["albumartist"] = message["track"]["album"]["artist"][0]["name"]
