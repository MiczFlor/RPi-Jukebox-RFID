"""Jellyfin player backend: Jellyfin catalog with MPD-based audio playback.

The backend owns its catalog and status while active and delegates the actual
audio transport and the coordinator's transport controls to the injected MPD
backend.
"""

import logging
import queue
import re
import threading
import time
from pathlib import Path

import jukebox.cfghandler
import jukebox.multitimer as multitimer
import jukebox.publishing as publishing


ALBUM_URI_PREFIX = 'service:jellyfin:album:'
TRACK_URI_PREFIX = 'service:jellyfin:track:'

#: Albums fetched per catalog page while building the cache. Keeps every
#: request bounded so large libraries cannot exhaust the request timeout.
ALBUM_PAGE_SIZE = 500

#: Seconds a failed cover download is not retried. Without this, the status
#: poller (0.25 s) would re-enqueue the same cover on every tick against an
#: offline server (~4 requests/second).
COVER_RETRY_DELAY = 60.0

#: Seconds a failed catalog fill is not retried. Waiting and concurrent
#: callers get the stale catalog (or an empty list on the very first fill)
#: during this window instead of each starting a new full fetch against a
#: server that just proved unreachable.
CATALOG_RETRY_DELAY = 30.0

#: Matches the item id inside a Jellyfin stream URL, e.g.
#: ``http://host/Audio/<id>/stream?static=true&api_key=...``. Used to recover
#: track metadata when MPD reports a normalized variant of the stream URL.
_STREAM_URL_ITEM_ID_RE = re.compile(r'/Audio/(?P<item_id>[^/?#]+)/stream')

logger = logging.getLogger('jb.player.jellyfin')


def component_id_from_uri(uri, prefix=None):
    """Extract the Jellyfin item id from a stable ``service:jellyfin:*`` URI.

    With ``prefix`` only that exact URI kind is matched; without it both the
    album and the track prefix are tried.
    """
    if not isinstance(uri, str):
        return None
    if prefix is not None:
        if uri.startswith(prefix):
            return uri[len(prefix):]
        return None
    for candidate in (ALBUM_URI_PREFIX, TRACK_URI_PREFIX):
        if uri.startswith(candidate):
            return uri[len(candidate):]
    return None


class JellyfinBackend:
    """Duck-typed player backend exposing a Jellyfin catalog and MPD playback."""

    def __init__(self, api, mpd, cache_ttl=300.0):
        self._api = api
        self._mpd = mpd
        self._active = False
        # stream URL -> {uri, title, artist, album, duration, track, item_id}
        self._stream_to_track = {}
        # item id -> track metadata (same entries, keyed by the stable item id
        # so a normalized MPD stream URL can still be resolved to a track).
        self._track_by_item_id = {}
        # track id -> album id, resolved from the server once for tracks that
        # were not seen this session (e.g. the playlist was restored after a
        # restart). Keeps covers on the per-album artwork instead of falling
        # back to a per-track cover.
        self._track_album_id = {}
        # Stream URLs that could not be mapped to a track and were masked from
        # the published status (throttles the warning to once per URL/playlist).
        self._unmapped_stream_warnings = set()
        self._catalog_cache = None
        self._catalog_cache_ts = 0.0
        self._cache_ttl = float(cache_ttl or 300)
        # Catalog cache access is guarded by a condition so a large library is
        # fetched by at most one thread at a time (background warm-up vs. RPC
        # requests) and callers never duplicate the network work.
        self._catalog_cond = threading.Condition()
        self._catalog_fetching = False
        # monotonic() timestamp until which a failed catalog fill is not
        # retried (negative caching, see _get_cached_albums).
        self._catalog_fetch_error_until = 0.0
        self._warmup_started = False
        self._cover_cache_dir = Path(
            jukebox.cfghandler.get_handler('jukebox').setndefault(
                'webapp', 'coverart_cache_path',
                value='../../src/webapp/build/cover-cache')
        ).expanduser()
        # Cover art is resolved lazily (memoized per item) and written by a
        # background worker so neither playback nor the status poller ever
        # blocks on network or disk I/O.
        self._cover_memo = {}
        # item id -> monotonic timestamp until which a failed download is not
        # retried (prevents a retry storm from the 0.25 s status poller).
        self._cover_retry_after = {}
        self._cover_write_queue = queue.Queue()
        self._cover_worker = threading.Thread(
            target=self._cover_worker_loop, daemon=True)
        self._cover_worker.start()
        self._status_timer = multitimer.GenericEndlessTimerClass(
            'jellyfin.timer_status', 0.25, self._publish_status)
        self._status_timer.start()

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    def exit(self):
        """Close the status poller and the HTTP session."""
        if self._status_timer is not None:
            self._status_timer.close()
            self._status_timer = None
        if self._api is not None:
            self._api.close()
            self._api = None
        self._catalog_cache = None
        self._catalog_cache_ts = 0.0

    # ------------------------------------------------------------------
    # Catalog
    # ------------------------------------------------------------------

    def library_source(self):
        return {
            'id': 'jellyfin',
            'label': 'Jellyfin',
            'views': [
                {'id': 'albums', 'label': 'Albums',
                 'kind': 'items', 'content_types': ['album']},
            ],
        }

    def list_library_items(self, content_types=None):
        if content_types is not None and 'album' not in content_types:
            return []
        items = []
        for album in self._get_cached_albums():
            album_id = album.get('Id')
            if not album_id:
                continue
            filename = self._peek_coverart(album_id)
            items.append({
                'provider': 'jellyfin',
                'content_type': 'album',
                'content_uri': f'{ALBUM_URI_PREFIX}{album_id}',
                'albumartist': album.get('AlbumArtist', ''),
                'album': album.get('Name', ''),
                'cover_url': f'/cover-cache/{filename}' if filename else None,
            })
        return items

    def _get_cached_albums(self):
        """Return the album catalog, refreshing it when the TTL expired.

        At most one thread fetches the catalog at a time. An expired catalog
        is refreshed in the background and the stale data is served meanwhile,
        so the WebApp/RPC path is never blocked for the full fetch duration.
        Callers arriving during the very first fill (start-up warm-up) wait
        for it to complete.

        A failed fill is negative-cached for :data:`CATALOG_RETRY_DELAY`
        seconds: during that window the stale catalog (or an empty list on the
        very first fill) is served instead of every caller starting a new full
        fetch against a server that just proved unreachable.
        """
        with self._catalog_cond:
            while True:
                now = time.monotonic()
                if (self._catalog_cache is not None
                        and now - self._catalog_cache_ts < self._cache_ttl):
                    return self._catalog_cache
                if self._catalog_cache is not None:
                    if now < self._catalog_fetch_error_until:
                        # The last refresh failed recently; serve the stale
                        # cache instead of spawning another refresh.
                        return self._catalog_cache
                    if self._catalog_fetching:
                        # In-flight refresh with a stale catalog: serve the
                        # stale data instead of blocking on the network.
                        return self._catalog_cache
                    # Expired: refresh in the background, serve stale data.
                    self._catalog_fetching = True
                    threading.Thread(
                        target=self._refresh_albums_worker,
                        name='jellyfin.catalog_refresh',
                        daemon=True,
                    ).start()
                    return self._catalog_cache
                if now < self._catalog_fetch_error_until:
                    # The last first-fill attempt failed; do not hammer the
                    # server with another full catalog fetch.
                    return []
                if self._catalog_fetching:
                    # First fill (start-up warm-up) still in progress; wait.
                    self._catalog_cond.wait()
                    continue
                self._catalog_fetching = True
                break
        return self._fetch_and_store_albums()

    def _fetch_and_store_albums(self):
        """Fetch the catalog and publish it to the cache (fetcher thread)."""
        try:
            albums = self._fetch_all_albums()
        except Exception as error:
            with self._catalog_cond:
                self._catalog_fetching = False
                self._catalog_fetch_error_until = (
                    time.monotonic() + CATALOG_RETRY_DELAY)
                self._catalog_cond.notify_all()
                if self._catalog_cache is not None:
                    logger.warning(
                        "Jellyfin catalog refresh failed; serving cached catalog: %s",
                        error)
                    return self._catalog_cache
            raise
        with self._catalog_cond:
            self._catalog_cache = albums
            self._catalog_cache_ts = time.monotonic()
            self._catalog_fetching = False
            self._catalog_fetch_error_until = 0.0
            self._catalog_cond.notify_all()
        self._prune_stale_covers()
        return albums

    def _refresh_albums_worker(self):
        """Background catalog refresh started when the TTL expired."""
        try:
            self._fetch_and_store_albums()
        except Exception as error:
            logger.warning("Jellyfin catalog background refresh failed: %s", error)

    def _prune_stale_covers(self):
        """Delete cached cover files whose item left the library.

        Runs after a successful catalog refresh. A cover file is kept when
        its item is part of the current album catalog or was referenced in
        this session; every other cached cover (e.g. from an album that was
        removed on the server) is deleted. Track covers are re-downloaded
        lazily when needed again.
        """
        if not self._cover_cache_dir.is_dir():
            return
        album_ids = {
            album.get('Id')
            for album in self._catalog_cache or []
            if album.get('Id')
        }
        removed = 0
        for path in self._cover_cache_dir.glob('jellyfin-*.jpg'):
            item_id = path.stem[len('jellyfin-'):]
            if item_id in album_ids or item_id in self._cover_memo:
                continue
            try:
                path.unlink()
                removed += 1
            except OSError as error:
                logger.warning(
                    "Could not remove stale Jellyfin cover %s: %s", path, error)
        if removed:
            logger.info("Removed %d stale Jellyfin cover file(s)", removed)

    def _fetch_all_albums(self):
        """Fetch the full album catalog in bounded pages.

        Requests a page of :data:`ALBUM_PAGE_SIZE` albums at a time so a
        large library never needs a single oversized request. Stops as soon
        as a page is shorter than the page size or a server keeps returning
        the identical page (i.e. it ignores the ``StartIndex``/``Limit``
        parameters), which would otherwise loop forever.
        """
        albums = []
        start_index = 0
        previous_page = []
        while True:
            page = self._api.get_albums(
                limit=ALBUM_PAGE_SIZE, start_index=start_index)
            albums.extend(page)
            if len(page) < ALBUM_PAGE_SIZE:
                break
            if page == previous_page:
                logger.warning(
                    "Jellyfin returned the identical catalog page for "
                    "StartIndex=%d; stopping pagination", start_index)
                break
            previous_page = page
            start_index += ALBUM_PAGE_SIZE
        return albums

    def start_warmup(self):
        """Prefetch the album catalog in the background at startup.

        With 1000+ albums the initial catalog fetch takes ~18 s on a local
        network, which exceeds the WebApp's request timeout. Warm-up runs only
        once and never on the RPC/plugin-call thread, so the first WebApp
        ``libraryItems`` request is served from a warm cache instead of
        blocking the player and RPC paths.
        """
        with self._catalog_cond:
            if self._warmup_started:
                return
            self._warmup_started = True
        threading.Thread(
            target=self._warmup_worker,
            name='jellyfin.catalog_warmup',
            daemon=True,
        ).start()

    def _warmup_worker(self):
        try:
            albums = self._get_cached_albums()
            logger.info(
                "Jellyfin catalog warmed up (%d album(s))", len(albums))
        except Exception as error:
            logger.warning("Jellyfin catalog warm-up failed: %s", error)

    def _find_album_id(self, albumartist, album):
        """Resolve an album item id from the cached catalog by name/artist."""
        if not album:
            return None
        for candidate in self._get_cached_albums():
            if candidate.get('Name') != album:
                continue
            if not albumartist:
                return candidate.get('Id')
            if (candidate.get('AlbumArtist') or '') == (albumartist or ''):
                return candidate.get('Id')
        return None

    def _content_uri_to_album_id(self, content_uri):
        if not content_uri:
            return None
        return component_id_from_uri(content_uri, prefix=ALBUM_URI_PREFIX)

    def list_songs_by_artist_and_album(
            self, albumartist, album, content_uri=None, provider=None):
        album_id = (self._content_uri_to_album_id(content_uri)
                    or self._find_album_id(albumartist, album))
        if album_id is None:
            return []
        try:
            tracks = self._api.get_album_children(album_id)
        except Exception as error:
            logger.error("Jellyfin song list failed: %s", error)
            return []
        return [
            self._track_metadata(track)
            for track in tracks
            if track.get('Id')
        ]

    def get_song_by_url(self, song_url, provider=None):
        track_id = component_id_from_uri(song_url)
        if track_id is None:
            return []
        try:
            item = self._api.get_item(track_id)
        except Exception as error:
            logger.error("Jellyfin get_song_by_url failed: %s", error)
            return []
        if not item or item.get('Type') != 'Audio':
            return []
        return [self._track_metadata(item)]

    def _track_metadata(self, item):
        """Return a unified track dict from a Jellyfin Audio item."""
        return {
            'provider': 'jellyfin',
            'album': item.get('Album', ''),
            'artist': ', '.join(item.get('Artists') or []),
            'title': item.get('Name', ''),
            'file': f'{TRACK_URI_PREFIX}{item["Id"]}',
            'track': item.get('IndexNumber'),
            'duration': (item.get('RunTimeTicks') or 0) // 10_000_000,
            'cover_url': None,
        }

    # ------------------------------------------------------------------
    # Playback
    # ------------------------------------------------------------------

    def play_album(self, albumartist, album, content_uri=None, provider=None):
        album_id = (self._content_uri_to_album_id(content_uri)
                    or self._find_album_id(albumartist, album))
        if album_id is None:
            logger.warning("Jellyfin album not found: '%s' by '%s'", album, albumartist)
            return
        try:
            tracks = self._api.get_album_children(album_id)
        except Exception as error:
            logger.error("Jellyfin play_album failed: %s", error)
            return
        stream_to_track = {
            self._api.get_stream_url(track['Id']): self._track_info(track)
            for track in tracks
            if track.get('Id')
        }
        self._play_streams(list(stream_to_track), stream_to_track)

    def play_single(self, song_url, provider=None):
        track_id = component_id_from_uri(song_url)
        if track_id is None:
            logger.warning("Invalid Jellyfin track URI: '%s'", song_url)
            return
        try:
            item = self._api.get_item(track_id)
        except Exception as error:
            logger.error("Jellyfin play_single failed: %s", error)
            return
        if not item:
            logger.warning("Jellyfin track not found: '%s'", song_url)
            return
        stream_url = self._api.get_stream_url(track_id)
        self._play_streams([stream_url], {stream_url: self._track_info(item)})

    def play_folder(self, folder, recursive=False):
        """Play an album or single-track URI supplied by a card swipe."""
        track_id = component_id_from_uri(folder, prefix=TRACK_URI_PREFIX)
        if track_id is not None:
            return self.play_single(folder)
        album_id = component_id_from_uri(folder, prefix=ALBUM_URI_PREFIX)
        if album_id is not None:
            return self.play_album(None, None, content_uri=folder)
        logger.warning("Unrecognized Jellyfin card value: '%s'", folder)

    def is_second_swipe(self, folder):
        """No second-swipe action for Jellyfin content."""
        return False

    def _track_info(self, item):
        """Unified track metadata for the stream->track status map."""
        return {
            'uri': f'{TRACK_URI_PREFIX}{item["Id"]}',
            'title': item.get('Name', ''),
            'artist': ', '.join(item.get('Artists') or []),
            'album': item.get('Album', ''),
            'duration': (item.get('RunTimeTicks') or 0) // 10_000_000,
            'track': item.get('IndexNumber'),
            'item_id': item['Id'],
            # Parent album id: covers are cached per album (one file per album,
            # identical artwork for every track), see _normalize_status and
            # get_single_coverart.
            'album_id': item.get('AlbumId', ''),
        }

    def _play_streams(self, stream_urls, stream_to_track=None):
        if not stream_urls:
            logger.warning("No Jellyfin streams to play")
            return
        try:
            self._mpd.clear_playlist()
            for url in stream_urls:
                self._mpd.add_to_playlist(url)
            self._mpd.play()
        except Exception as error:
            # Leave the stream->track mapping untouched so a partially built
            # playlist can never masquerade as the Jellyfin playlist.
            logger.error(
                "Jellyfin playback failed while building the MPD playlist: %s",
                error)
            return
        # Remember the stream URL -> track-metadata mapping for playerstatus.
        # Set on every playback path (album and single track) so the
        # normalized status never exposes the raw stream URL (API key).
        self._stream_to_track = stream_to_track or {}
        # Secondary index by item id: if MPD reports a normalized variant of a
        # stream URL (exact match fails), the track metadata can still be
        # recovered from the item id embedded in the URL (see _normalize_status).
        self._track_by_item_id = {
            track['item_id']: track
            for track in self._stream_to_track.values()
            if track.get('item_id')
        }
        self._unmapped_stream_warnings = set()
        logger.info("Playing %d Jellyfin stream(s)", len(stream_urls))

    # ------------------------------------------------------------------
    # Cover art
    # ------------------------------------------------------------------

    def get_single_coverart(self, song_url, provider=None):
        track_id = component_id_from_uri(song_url)
        if track_id is None:
            # Defensive: a client may pass the raw MPD stream URL instead of
            # the stable URI — reverse-map it.
            track = self._stream_to_track.get(song_url)
            if track is not None:
                track_id = component_id_from_uri(track['uri'])
        if track_id is None and isinstance(song_url, str):
            # A raw stream URL for a track not seen this session (e.g. after
            # a restart): the item id is embedded in the URL.
            match = _STREAM_URL_ITEM_ID_RE.search(song_url)
            if match:
                track_id = match.group('item_id')
        if track_id is None:
            return None
        # Prefer the album cover so the cache keeps one file per album (the
        # artwork is identical for every track). The track metadata is only
        # known for items seen this session; for any other track the album id
        # is resolved from the server once so the already-cached album artwork
        # is reused instead of downloading a per-track cover.
        track = self._track_by_item_id.get(track_id) or {}
        item_id = track.get('album_id') or self._resolve_album_id(track_id)
        return self._cache_coverart(item_id or track_id)

    def get_album_coverart(self, albumartist, album, content_uri=None, provider=None):
        album_id = (self._content_uri_to_album_id(content_uri)
                    or self._find_album_id(albumartist, album))
        return self._cache_coverart(album_id) if album_id else None

    def _resolve_album_id(self, track_id):
        """Return the album id a track belongs to, resolving it once.

        Tracks are only mapped to their album while a playlist built by this
        backend is playing. After a restart (MPD restores the playlist, the
        in-memory map is empty) the album id is fetched from the server once
        and memoized, so covers keep resolving to the per-album artwork.
        """
        if track_id in self._track_album_id:
            return self._track_album_id[track_id]
        album_id = None
        try:
            item = self._api.get_item(track_id)
        except Exception as error:
            logger.warning(
                "Could not resolve the album for track %s: %s",
                track_id, error)
        else:
            album_id = (item or {}).get('AlbumId') or None
        self._track_album_id[track_id] = album_id
        return album_id

    @staticmethod
    def _cover_filename(item_id):
        return f'jellyfin-{item_id}.jpg'

    def _peek_coverart(self, item_id):
        """Return the cached cover filename for ``item_id`` without downloading.

        Like :meth:`_cache_coverart` for covers already on disk, but never
        enqueues a download: used to attach ``cover_url`` to catalog items so
        the WebApp renders cached covers immediately. Items without a cached
        cover keep ``cover_url`` ``None`` and are resolved lazily through
        ``get_album_coverart``/``get_single_coverart`` as before.
        """
        if item_id is None:
            return None
        if item_id in self._cover_memo:
            return self._cover_memo[item_id] or None
        if time.monotonic() < self._cover_retry_after.get(item_id, 0.0):
            # A previous download failed recently; do not re-enqueue yet.
            return None
        filename = self._cover_filename(item_id)
        if (self._cover_cache_dir / filename).is_file():
            self._cover_memo[item_id] = filename
            return filename
        return None

    def _cache_coverart(self, item_id):
        """Return the cached cover filename for ``item_id``, downloading lazily.

        Memoized (at most one download per item) and non-blocking. Covers
        already present in the cache directory are reused immediately, so a
        restart does not require re-downloading. The first call for a missing
        cover enqueues the download on the background worker and returns
        ``None``; later calls return the bare filename once the worker has
        finished. A failed download is not retried for ``COVER_RETRY_DELAY``
        seconds, so the 0.25 s status poller cannot hammer a failing server.
        """
        if item_id is None:
            return None
        if item_id in self._cover_memo:
            return self._cover_memo[item_id] or None
        if time.monotonic() < self._cover_retry_after.get(item_id, 0.0):
            # A previous download failed recently; do not re-enqueue yet.
            return None
        filename = self._cover_filename(item_id)
        if (self._cover_cache_dir / filename).is_file():
            self._cover_memo[item_id] = filename
            return filename
        self._cover_memo[item_id] = None
        self._cover_write_queue.put(item_id)
        return None

    def _cover_worker_loop(self):
        """Background worker downloading and writing cover images."""
        while True:
            item_id = self._cover_write_queue.get()
            try:
                image_bytes = self._api.get_coverart_bytes(item_id)
                filename = self._cover_filename(item_id)
                self._cover_cache_dir.mkdir(parents=True, exist_ok=True)
                (self._cover_cache_dir / filename).write_bytes(image_bytes)
            except Exception as error:
                logger.warning(
                    "Could not fetch Jellyfin cover art for %s: %s", item_id, error)
                # Forget the pending entry and apply a cooldown, so the status
                # poller does not retry the download on every tick.
                self._cover_memo.pop(item_id, None)
                self._cover_retry_after[item_id] = time.monotonic() + COVER_RETRY_DELAY
            else:
                self._cover_memo[item_id] = filename
                self._cover_retry_after.pop(item_id, None)
            finally:
                self._cover_write_queue.task_done()

    def _cover_url(self, item_id):
        """Prefixed ``/cover-cache/`` URL for the playerstatus cover field."""
        filename = self._cache_coverart(item_id)
        return f'/cover-cache/{filename}' if filename else None

    # ------------------------------------------------------------------
    # Status
    # ------------------------------------------------------------------

    def set_active(self, active):
        self._active = active
        if active:
            self._publish_status()

    def _publish_status(self):
        try:
            if not self._active or self._mpd is None:
                return
            mpd_status = dict(self._mpd.mpd_status)
            publishing.get_publisher().send(
                'playerstatus', self._normalize_status(mpd_status))
        except Exception as error:
            # Never let a failing status poll kill the endless timer worker
            # (the timer framework has no error handling around callbacks).
            logger.exception("Jellyfin status publish failed: %s", error)

    def _normalize_status(self, mpd_status):
        """Build the complete status from MPD state and Jellyfin metadata."""
        file_url = mpd_status.get('file')
        track = self._stream_to_track.get(file_url)
        stream_match = None
        if track is None and isinstance(file_url, str):
            # MPD may normalize the stream URL (query order, path), so the
            # exact lookup above can miss. Recover the metadata from the item
            # id that is embedded in the stream URL.
            stream_match = _STREAM_URL_ITEM_ID_RE.search(file_url)
            if stream_match:
                track = self._track_by_item_id.get(stream_match.group('item_id'))
        if track is None:
            track = {}
            if self._is_stream_url(file_url):
                # A Jellyfin stream URL that could not be mapped to a track
                # must never surface on an RPC/publish channel (it carries the
                # API key/token). Mask it and warn once per URL.
                self._warn_unmapped_stream(file_url)
                file_url = ''
        cover_item_id = track.get('album_id') or track.get('item_id')
        if cover_item_id is None and stream_match is not None:
            # The track was not seen this session (e.g. MPD restored the
            # playlist after a restart): resolve the album from the item id
            # embedded in the stream URL so the published cover always matches
            # the per-album artwork.
            cover_item_id = self._resolve_album_id(
                stream_match.group('item_id'))
        return {
            'state': mpd_status.get('state', 'stop'),
            'songid': track.get('uri') or mpd_status.get('songid'),
            'song': mpd_status.get('song', ''),
            'elapsed': mpd_status.get('elapsed', '0.0'),
            'random': mpd_status.get('random', '0'),
            'repeat': mpd_status.get('repeat', '0'),
            'single': mpd_status.get('single', '0'),
            'title': track.get('title', ''),
            'artist': track.get('artist', ''),
            'album': track.get('album', ''),
            'duration': str(track.get('duration', 0)),
            'file': track.get('uri') or file_url,
            'provider': 'jellyfin',
            'cover_url': self._cover_url(cover_item_id),
        }

    @classmethod
    def _is_stream_url(cls, file_url):
        """Return whether ``file_url`` looks like a Jellyfin stream URL."""
        return (
            isinstance(file_url, str)
            and _STREAM_URL_ITEM_ID_RE.search(file_url) is not None
        )

    def _warn_unmapped_stream(self, file_url):
        """Log a throttled warning for a stream URL that could not be mapped.

        The warning never contains the URL itself (it carries the API key).
        """
        if file_url in self._unmapped_stream_warnings:
            return
        self._unmapped_stream_warnings.add(file_url)
        match = _STREAM_URL_ITEM_ID_RE.search(file_url)
        item_id = match.group('item_id') if match else 'unknown'
        logger.warning(
            "MPD is playing a Jellyfin stream for item '%s' that is not mapped "
            "to a track; hiding the stream URL from the published status",
            item_id)

    def get_player_type_and_version(self):
        return self._mpd.get_player_type_and_version()

    # ------------------------------------------------------------------
    # Active-backend delegation to MPD
    # ------------------------------------------------------------------

    def stop(self):
        return self._mpd.stop()

    def play(self):
        return self._mpd.play()

    def pause(self, state=1):
        return self._mpd.pause(state)

    def prev(self):
        return self._mpd.prev()

    def next(self):
        return self._mpd.next()

    def seek(self, new_time):
        return self._mpd.seek(new_time)

    def rewind(self):
        return self._mpd.rewind()

    def replay(self):
        """Restart the current Jellyfin track from the beginning."""
        self._mpd.seek(0)
        return self._mpd.play()

    def toggle(self):
        return self._mpd.toggle()

    def replay_if_stopped(self):
        """Restart the current Jellyfin playlist if MPD is stopped."""
        if self._mpd.mpd_status.get('state') == 'stop':
            return self._mpd.rewind()

    def resume(self):
        """Resume the current Jellyfin playlist from the saved position."""
        songpos = self._mpd.mpd_status.get('song', 0)
        elapsed = self._mpd.mpd_status.get('elapsed', '0')
        with self._mpd.mpd_lock:
            self._mpd.mpd_client.seek(songpos, elapsed)
            self._mpd.mpd_client.play()

    def shuffle(self, option='toggle'):
        return self._mpd.shuffle(option)

    def repeat(self, option='toggle'):
        return self._mpd.repeat(option)

    def get_current_song(self, param=None):
        status = self._normalize_status(self._mpd.playerstatus())
        return status.get(param) if param else status

    def playerstatus(self):
        return self._normalize_status(self._mpd.playerstatus())

    def playlistinfo(self):
        return [self._normalize_status(self._mpd.playerstatus())]

    def get_volume(self):
        return self._mpd.get_volume()

    def set_volume(self, volume):
        return self._mpd.set_volume(volume)
