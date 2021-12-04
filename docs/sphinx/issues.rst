Known Issues
******************

Browsers
----------

The Web UI will **not** work with Firefox, due to an issue with websockets and pyzmq. Please use a different
browser for now.

Configuration
--------------
In ``jukebox.yaml`` (and all other config files): do not use paths with ``~/some/dir``.
Always use entire explicit path, e.g. ``/home/pi/some/dir``.

**Sole** exception is in playermpd.mpd_conf.
