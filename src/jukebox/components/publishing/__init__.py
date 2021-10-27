"""
Plugin interface for Jukebox Publisher

Thin wrapper around jukebox.publishing to benefit from the plugin loading / exit handling / function handling

This is the first package to be loaded and the last to be closed: put Hello and Goodbye publish messages here.

"""

import logging
import jukebox
import jukebox.cfghandler
import jukebox.plugs as plugin
import jukebox.publishing as pub

logger = logging.getLogger('jb.pub')
cfg = jukebox.cfghandler.get_handler('jukebox')

# Create the one global proxy server instance that handles client connections and Last-Value-Caching
_PUBLISH_SERVER_THREAD: pub.server.PublishServer


@plugin.register
def republish(topic=None):
    """Re-publish the topic tree 'topic' to all subscribers

    :param topic: Topic tree to republish. None = resend all"""
    pub.get_publisher().resend(topic)


@plugin.initialize
def initialize():
    global _PUBLISH_SERVER_THREAD
    tcp_port = cfg.setndefault('publishing', 'tcp_port', value=5558)
    ws_port = cfg.setndefault('publishing', 'websocket_port', value=5566)
    _PUBLISH_SERVER_THREAD = pub.server.PublishServer(tcp_port=tcp_port, websocket_port=ws_port)
    _PUBLISH_SERVER_THREAD.start()
    pub.get_publisher().send('core.welcome', 'Welcome! Let the sound begin')
    pub.get_publisher().send('core.version', jukebox.version())


@plugin.atexit
def closing(**ignored_kwargs):
    global _PUBLISH_SERVER_THREAD
    logger.debug("Closing publish server connection")
    pub.get_publisher().send('core.welcome', 'Goodbye. Hear you later!')
    pub.get_publisher().close_server()
    return _PUBLISH_SERVER_THREAD
