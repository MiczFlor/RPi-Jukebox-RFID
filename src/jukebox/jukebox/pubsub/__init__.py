import jukebox.pubsub.server as server


class _PubSubBuilder:

    def __init__(self):
        self._instance = None

    def __call__(self, *args, **kwargs):
        if not self._instance:
            self._instance = server.PubSubServer()
        return self._instance


# _pubsubbuilder: = _PubSubBuilder()
#
#
# def get_publisher():
#     return _pubsubbuilder()
