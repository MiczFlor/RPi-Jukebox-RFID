# Sleep timer plugin for the Jukebox player.
#
# Stops playback automatically after a configurable number of seconds -- handy e.g. for children
# listening to audiobooks at bedtime. This is a thin wrapper around the core `timers` component's
# `timer_stop_player`, exposed under a friendlier name/interface for the player webview.
import jukebox.plugs as plugin

# Ships its own webapp UI (see static/ui.js) for the player view's "player" slot, instead of requiring
# changes to the webapp's own source -- see components.webui_plugins and
# documentation/developers/webui-plugins.md.
PLUGIN_UI_SLOT = 'player'
PLUGIN_UI_ENTRY = 'ui.js'


@plugin.register
def start(wait_seconds: float):
    """Start (or restart) the sleep timer: stop playback in `wait_seconds` seconds"""
    plugin.call('timers', 'timer_stop_player', 'start', args=[wait_seconds])


@plugin.register
def cancel():
    """Cancel a running sleep timer"""
    plugin.call('timers', 'timer_stop_player', 'cancel')


@plugin.register
def get_state():
    """Get the current sleep timer state (enabled, remaining_seconds, wait_seconds, type)"""
    return plugin.call('timers', 'timer_stop_player', 'get_state')
