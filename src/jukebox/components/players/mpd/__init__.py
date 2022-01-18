import logging
import mpd

logger = logging.getLogger('jb.players.mpd')

# MPD Interface
class MpdPlayer:
    def __init__(self):
        logger.debug('Init MPD')
        self.mpd_client = mpd.MPDClient() # This is pseudo code, not functionl yet

    def play_single(self, uri: str):
        self.mpd_client.clear()
        self.mpd_client.addid(uri)
        self.mpd_client.play()


class MpdPlayerBuilder:
    def __init__(self):
        self._instance = None

    def __call__(self, **_ignored):
        if not self._instance:
            self._instance = MpdPlayer()

        return self._instance
