# RPi-Jukebox-RFID Version 3
# Copyright (c) See file LICENSE in project root folder
"""
Serves webapp UI extensions that plugins ship themselves.

A plugin (core or user) can bring its own small UI bundle for the webapp instead of requiring changes to
the webapp's own source code. It does so by declaring two module-level attributes in its package's
``__init__.py``::

    PLUGIN_UI_SLOT = 'player'      # which webapp UI slot to extend, e.g. 'player'
    PLUGIN_UI_ENTRY = 'ui.js'      # entry point file, relative to a `static/` dir next to __init__.py

and shipping that entry point (plus whatever else it needs) under ``static/`` alongside its Python code.
The entry point module must export two functions, ``mount(container, sdk)`` and ``unmount(container)`` --
see the ``sleep_timer`` example plugin (``plugins/sleep_timer``) for a worked example, and
``documentation/developers/webui-plugins.md`` for the full contract.

This component collects that metadata from all loaded plugins (once, after all of them have been loaded)
and serves each plugin's ``static/`` directory over a small dedicated HTTP server, so the webapp can fetch
and dynamically load the bundles at runtime without needing to know about them at build time.
"""
import asyncio
import logging
import threading
from pathlib import Path
from typing import Any, Dict, List, Optional

import tornado.httpserver
import tornado.web
from tornado.ioloop import IOLoop

import jukebox.cfghandler
import jukebox.plugs as plugin

logger = logging.getLogger('jb.webui_plugins')
cfg = jukebox.cfghandler.get_handler('jukebox')


class _UiExtensionServer(threading.Thread):
    """Tiny static file server, one route per plugin, serving its `static/` directory

    Runs in a dedicated thread with its own, freshly created event loop -- NOT the shared
    `zmq.eventloop.ioloop.IOLoop.instance()` singleton that jukebox.publishing.server.PublishServer
    uses, since that singleton is process-wide and can only be started/run from one thread at a time.
    All tornado setup happens inside run(), in the new thread, not in __init__ (which runs on the
    thread that calls `finalize()`).
    """

    def __init__(self, port: int, static_dirs: Dict[str, Path]):
        super().__init__(name='WebUiPluginServer')
        self.daemon = True
        self._port = port
        self._static_dirs = static_dirs
        self.loop = None

    def run(self):
        """Thread's activity"""
        asyncio.set_event_loop(asyncio.new_event_loop())
        self.loop = IOLoop.current()
        handlers = [
            (rf"/{name}/(.*)", tornado.web.StaticFileHandler, {'path': str(path)})
            for name, path in self._static_dirs.items()
        ]
        app = tornado.web.Application(handlers)
        server = tornado.httpserver.HTTPServer(app)
        server.listen(self._port)
        logger.info(f"Serving {len(self._static_dirs)} webapp UI plugin bundle(s) on port {self._port}: "
                    f"{', '.join(self._static_dirs.keys())}")
        self.loop.start()

    def stop(self):
        if self.loop is not None:
            self.loop.add_callback(self.loop.stop)


_server: Optional[_UiExtensionServer] = None
_manifest: List[Dict[str, Any]] = []


@plugin.finalize
def finalize():
    """Collect UI extension metadata from all loaded plugins and start serving their static assets

    Must run after all core and user plugins have been loaded (i.e. as a `@plugin.finalize`), so that
    plugins loaded after this component (in particular all user plugins) are seen too.
    """
    global _server, _manifest
    port = cfg.setndefault('webui_plugins', 'port', value=5559)
    host = cfg.setndefault('webui_plugins', 'host', value='localhost')

    static_dirs = {}
    for name in plugin.get_all_loaded_packages():
        module = plugin.get_module(name)
        slot = getattr(module, 'PLUGIN_UI_SLOT', None)
        entry = getattr(module, 'PLUGIN_UI_ENTRY', None)
        if slot is None or entry is None:
            continue
        static_dir = Path(module.__file__).resolve().parent / 'static'
        if not (static_dir / entry).is_file():
            logger.error(f"Plugin '{name}' declares UI extension '{entry}' for slot '{slot}', "
                        f"but '{static_dir / entry}' does not exist. Skipping.")
            continue
        static_dirs[name] = static_dir
        _manifest.append({'name': name, 'slot': slot, 'url': f"http://{host}:{port}/{name}/{entry}"})

    if static_dirs:
        _server = _UiExtensionServer(port, static_dirs)
        _server.start()


@plugin.register
def get_manifest() -> List[Dict[str, Any]]:
    """Get the list of installed webapp UI plugin extensions: [{name, slot, url}, ...]"""
    return _manifest


@plugin.atexit
def atexit(**ignored_kwargs):
    if _server is not None:
        _server.stop()
