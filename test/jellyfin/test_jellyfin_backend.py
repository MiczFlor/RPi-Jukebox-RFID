import threading
import time
from contextlib import nullcontext
from types import SimpleNamespace
from unittest.mock import Mock, call, patch

import pytest

import jukebox.cfghandler as cfghandler
import jukebox.publishing as publishing

from components.jellyfin import configure_jellyfin
from components.jellyfin.jellyfin_api_client import DEFAULT_TIMEOUT
from components.jellyfin.jellyfin_backend import (
    ALBUM_PAGE_SIZE,
    ALBUM_URI_PREFIX,
    TRACK_URI_PREFIX,
    JellyfinBackend,
    component_id_from_uri,
)

STREAM_URL = 'http://jellyfin.local:8096/Audio/{item_id}/stream?static=true&api_key=key'


class FakeTimer:
    def __init__(self, name, interval, callback):
        self.callback = callback
        self.closed = False

    def start(self):
        pass

    def close(self):
        self.closed = True


def make_api():
    api = Mock()
    api.get_albums.return_value = []
    api.get_album_children.return_value = []
    api.get_item.return_value = None
    api.get_stream_url.side_effect = lambda item_id: STREAM_URL.format(item_id=item_id)
    api.get_coverart_bytes.return_value = b'jpg-bytes'
    return api


def make_mpd():
    return SimpleNamespace(
        mpd_status={},
        mpd_lock=nullcontext(),
        mpd_client=SimpleNamespace(seek=Mock(), play=Mock()),
        stop=Mock(),
        play=Mock(),
        pause=Mock(),
        prev=Mock(),
        next=Mock(),
        seek=Mock(),
        rewind=Mock(),
        toggle=Mock(),
        shuffle=Mock(),
        repeat=Mock(),
        get_volume=Mock(return_value=70),
        set_volume=Mock(),
        get_player_type_and_version=Mock(return_value='MPD'),
        playerstatus=Mock(return_value={}),
        clear_playlist=Mock(),
        add_to_playlist=Mock(),
    )


def make_backend(api=None, mpd=None, cache_ttl=300.0):
    with patch('jukebox.multitimer.GenericEndlessTimerClass', FakeTimer):
        backend = JellyfinBackend(
            api if api is not None else make_api(),
            mpd if mpd is not None else make_mpd(),
            cache_ttl,
        )
    return backend


def reset_cfg(data=None):
    cfg = cfghandler.get_handler('jukebox')
    cfg.config_dict(data if data is not None else {})
    return cfg


def album_item(**overrides):
    item = {
        'Id': 'album-1',
        'Name': 'Album One',
        'AlbumArtist': 'Artist One',
    }
    item.update(overrides)
    return item


def track_item(**overrides):
    item = {
        'Id': 'track-1',
        'Name': 'Track One',
        'Type': 'Audio',
        'Artists': ['Artist One'],
        'Album': 'Album One',
        'AlbumId': 'album-1',
        'IndexNumber': 1,
        'RunTimeTicks': 123_000_000,
    }
    item.update(overrides)
    return item

# ---------------------------------------------------------------------------
# Catalog
# ---------------------------------------------------------------------------


def test_library_source_describes_albums_view():
    backend = make_backend()

    assert backend.library_source() == {
        'id': 'jellyfin',
        'label': 'Jellyfin',
        'views': [
            {'id': 'albums', 'label': 'Albums',
             'kind': 'items', 'content_types': ['album']},
        ],
    }


def test_list_library_items_maps_albums(tmp_path):
    api = make_api()
    api.get_albums.return_value = [
        album_item(),
        album_item(Id='album-2', Name='Album Two', AlbumArtist='Artist Two'),
    ]
    backend = make_backend(api)
    backend._cover_cache_dir = tmp_path

    assert backend.list_library_items(['album']) == [
        {
            'provider': 'jellyfin',
            'content_type': 'album',
            'content_uri': f'{ALBUM_URI_PREFIX}album-1',
            'albumartist': 'Artist One',
            'album': 'Album One',
            'cover_url': None,
        },
        {
            'provider': 'jellyfin',
            'content_type': 'album',
            'content_uri': f'{ALBUM_URI_PREFIX}album-2',
            'albumartist': 'Artist Two',
            'album': 'Album Two',
            'cover_url': None,
        },
    ]


def test_list_library_items_includes_cached_cover_url(tmp_path):
    api = make_api()
    api.get_albums.return_value = [
        album_item(),
        album_item(Id='album-2', Name='Album Two', AlbumArtist='Artist Two'),
    ]
    backend = make_backend(api)
    backend._cover_cache_dir = tmp_path
    (tmp_path / 'jellyfin-album-1.jpg').write_bytes(b'cached-cover')

    items = backend.list_library_items(['album'])

    # The album whose cover is already on disk ships the URL with the
    # catalog entry; the uncached album stays None (resolved lazily).
    assert items[0]['cover_url'] == '/cover-cache/jellyfin-album-1.jpg'
    assert items[1]['cover_url'] is None
    api.get_coverart_bytes.assert_not_called()
    assert backend._cover_write_queue.empty()


def test_list_library_items_does_not_enqueue_missing_covers(tmp_path):
    api = make_api()
    api.get_albums.return_value = [album_item()]
    backend = make_backend(api)
    backend._cover_cache_dir = tmp_path

    items = backend.list_library_items(['album'])

    # Listing the catalog must not trigger a bulk cover download; the
    # WebApp requests each missing cover on demand via get_album_coverart.
    assert items[0]['cover_url'] is None
    api.get_coverart_bytes.assert_not_called()
    assert backend._cover_write_queue.empty()


def test_list_library_items_honors_content_types_filter():
    api = make_api()
    api.get_albums.return_value = [album_item()]
    backend = make_backend(api)

    assert backend.list_library_items(['playlist']) == []
    api.get_albums.assert_not_called()


def test_list_library_items_uses_cached_catalog():
    api = make_api()
    api.get_albums.return_value = [album_item()]
    backend = make_backend(api)

    backend.list_library_items(['album'])
    backend.list_library_items(['album'])

    api.get_albums.assert_called_once_with(
        limit=ALBUM_PAGE_SIZE, start_index=0)


def test_catalog_fetch_paginates_through_pages():
    api = make_api()
    api.get_albums.side_effect = [
        [album_item(Id=f'album-{i}') for i in range(ALBUM_PAGE_SIZE)],
        [album_item(Id='album-extra', Name='Extra Album')],
    ]
    backend = make_backend(api)

    items = backend.list_library_items(['album'])

    assert len(items) == ALBUM_PAGE_SIZE + 1
    api.get_albums.assert_has_calls([
        call(limit=ALBUM_PAGE_SIZE, start_index=0),
        call(limit=ALBUM_PAGE_SIZE, start_index=ALBUM_PAGE_SIZE),
    ])


def test_fetch_all_albums_stops_when_server_ignores_pagination():
    api = make_api()
    full_page = [album_item()] * ALBUM_PAGE_SIZE
    api.get_albums.return_value = full_page
    backend = make_backend(api)

    albums = backend._fetch_all_albums()

    # The identical-page guard stops the loop after two pages instead of
    # looping forever against a server that ignores StartIndex/Limit.
    assert api.get_albums.call_count == 2
    assert len(albums) == ALBUM_PAGE_SIZE * 2


def test_catalog_cache_expiry_refetches_in_background():
    api = make_api()
    api.get_albums.return_value = [album_item()]
    backend = make_backend(api)

    backend.list_library_items(['album'])
    backend._catalog_cache_ts = time.monotonic() - 301.0
    backend.list_library_items(['album'])

    # The expired catalog is served immediately and refreshed in the
    # background; wait for the refresh so the fetch count is deterministic.
    deadline = time.monotonic() + 2.0
    while backend._catalog_fetching and time.monotonic() < deadline:
        time.sleep(0.01)

    assert api.get_albums.call_count == 2


def test_catalog_cache_serves_stale_catalog_on_refresh_error():
    api = make_api()
    api.get_albums.side_effect = [RuntimeError('offline')]
    backend = make_backend(api)
    backend._catalog_cache = [album_item()]
    backend._catalog_cache_ts = time.monotonic() - 301.0

    items = backend.list_library_items(['album'])

    assert len(items) == 1
    assert items[0]['content_uri'] == f'{ALBUM_URI_PREFIX}album-1'

    # The failed refresh runs in the background and leaves the stale cache.
    deadline = time.monotonic() + 2.0
    while backend._catalog_fetching and time.monotonic() < deadline:
        time.sleep(0.01)
    assert backend._catalog_cache == [album_item()]


def test_start_warmup_populates_catalog_in_background():
    api = make_api()
    api.get_albums.return_value = [album_item()]
    backend = make_backend(api)

    backend.start_warmup()

    deadline = time.monotonic() + 2.0
    while backend._catalog_cache is None and time.monotonic() < deadline:
        time.sleep(0.01)

    assert backend._catalog_cache == [album_item()]
    api.get_albums.assert_called_once_with(
        limit=ALBUM_PAGE_SIZE, start_index=0)


def test_start_warmup_is_idempotent():
    api = make_api()
    api.get_albums.return_value = [album_item()]
    backend = make_backend(api)

    backend.start_warmup()
    backend.start_warmup()

    deadline = time.monotonic() + 2.0
    while backend._catalog_cache is None and time.monotonic() < deadline:
        time.sleep(0.01)

    assert api.get_albums.call_count == 1


def test_catalog_fetch_is_not_duplicated_by_concurrent_callers():
    api = make_api()
    started = threading.Event()
    release = threading.Event()

    def slow_get_albums(limit, start_index=None):
        started.set()
        assert release.wait(2.0)
        return [album_item()]

    api.get_albums.side_effect = slow_get_albums
    backend = make_backend(api)
    results = []

    def fetch():
        results.append(backend._get_cached_albums())

    first = threading.Thread(target=fetch)
    second = threading.Thread(target=fetch)
    first.start()
    assert started.wait(2.0)
    second.start()
    time.sleep(0.05)  # let the second caller reach the condition wait
    release.set()
    first.join(2.0)
    second.join(2.0)

    assert not first.is_alive()
    assert not second.is_alive()
    assert api.get_albums.call_count == 1
    assert results == [[album_item()], [album_item()]]


def test_catalog_first_fill_failure_is_not_retried_within_cooldown():
    api = make_api()
    api.get_albums.side_effect = RuntimeError('offline')
    backend = make_backend(api)

    with pytest.raises(RuntimeError):
        backend._get_cached_albums()

    # A subsequent call within the cooldown window returns an empty catalog
    # instead of triggering a second full fetch.
    assert backend._get_cached_albums() == []
    assert api.get_albums.call_count == 1


def test_catalog_failure_is_negative_cached_for_waiting_callers():
    api = make_api()
    api.get_albums.side_effect = RuntimeError('offline')
    backend = make_backend(api)
    results = []

    def fetch():
        try:
            results.append(('result', backend._get_cached_albums()))
        except Exception as error:
            results.append(('error', type(error).__name__))

    first = threading.Thread(target=fetch)
    second = threading.Thread(target=fetch)
    first.start()
    # Let the first caller reach the synchronous first fill (and fail).
    deadline = time.monotonic() + 2.0
    while backend._catalog_fetching is False and time.monotonic() < deadline:
        time.sleep(0.01)
    second.start()
    first.join(2.0)
    second.join(2.0)

    # Only one fetch happened: the waiting caller got the negative-cached
    # empty catalog instead of starting its own full fetch.
    assert api.get_albums.call_count == 1
    assert ('error', 'RuntimeError') in results
    assert ('result', []) in results


def test_catalog_refresh_prunes_stale_covers(tmp_path):
    api = make_api()
    api.get_albums.return_value = [album_item()]
    backend = make_backend(api)
    backend._cover_cache_dir = tmp_path
    (tmp_path / 'jellyfin-album-1.jpg').write_bytes(b'kept-album')
    (tmp_path / 'jellyfin-album-gone.jpg').write_bytes(b'stale-album')
    (tmp_path / 'jellyfin-track-1.jpg').write_bytes(b'kept-track')
    backend._cover_memo = {'track-1': 'jellyfin-track-1.jpg'}

    backend.list_library_items(['album'])
    backend._catalog_cache_ts = time.monotonic() - 301.0
    backend.list_library_items(['album'])

    # Pruning runs after the background refresh of the expired catalog.
    deadline = time.monotonic() + 2.0
    while backend._catalog_fetching and time.monotonic() < deadline:
        time.sleep(0.01)

    assert (tmp_path / 'jellyfin-album-1.jpg').exists()
    assert (tmp_path / 'jellyfin-track-1.jpg').exists()
    assert not (tmp_path / 'jellyfin-album-gone.jpg').exists()


def test_catalog_fresh_cache_does_not_prune(tmp_path):
    api = make_api()
    api.get_albums.return_value = [album_item()]
    backend = make_backend(api)
    backend._cover_cache_dir = tmp_path

    backend.list_library_items(['album'])
    (tmp_path / 'jellyfin-album-gone.jpg').write_bytes(b'stale-album')
    backend.list_library_items(['album'])

    assert (tmp_path / 'jellyfin-album-gone.jpg').exists()


def test_find_album_id_by_name_and_artist():
    api = make_api()
    api.get_albums.return_value = [album_item()]
    backend = make_backend(api)

    assert backend._find_album_id('Artist One', 'Album One') == 'album-1'
    assert backend._find_album_id('', 'Album One') == 'album-1'
    assert backend._find_album_id('Other', 'Album One') is None
    assert backend._find_album_id(None, '') is None


def test_list_songs_by_artist_and_album_uses_content_uri():
    api = make_api()
    api.get_album_children.return_value = [track_item()]
    backend = make_backend(api)

    songs = backend.list_songs_by_artist_and_album(
        None, None, content_uri=f'{ALBUM_URI_PREFIX}album-1')

    assert songs == [{
        'provider': 'jellyfin',
        'album': 'Album One',
        'artist': 'Artist One',
        'title': 'Track One',
        'file': f'{TRACK_URI_PREFIX}track-1',
        'track': 1,
        'duration': 12,
        'cover_url': None,
    }]


def test_list_songs_content_uri_precedence_over_name_lookup():
    api = make_api()
    api.get_albums.return_value = [album_item()]
    api.get_album_children.return_value = [track_item()]
    backend = make_backend(api)

    backend.list_songs_by_artist_and_album(
        'Artist One', 'Album One', content_uri=f'{ALBUM_URI_PREFIX}album-1')

    api.get_album_children.assert_called_once_with('album-1')


def test_list_songs_missing_duration_does_not_raise():
    api = make_api()
    api.get_album_children.return_value = [track_item(RunTimeTicks=None)]
    backend = make_backend(api)

    songs = backend.list_songs_by_artist_and_album(
        None, None, content_uri=f'{ALBUM_URI_PREFIX}album-1')

    assert songs[0]['duration'] == 0


def test_get_song_by_url():
    api = make_api()
    api.get_item.return_value = track_item()
    backend = make_backend(api)

    songs = backend.get_song_by_url(f'{TRACK_URI_PREFIX}track-1')

    assert len(songs) == 1
    assert songs[0]['file'] == f'{TRACK_URI_PREFIX}track-1'
    assert songs[0]['provider'] == 'jellyfin'


def test_get_song_by_url_bad_uri():
    backend = make_backend()

    assert backend.get_song_by_url('service:foo:track-1') == []


def test_get_song_by_url_ignores_non_audio_items():
    api = make_api()
    api.get_item.return_value = {'Id': 'movie-1', 'Type': 'Movie', 'Name': 'Film'}
    backend = make_backend(api)

    assert backend.get_song_by_url(f'{TRACK_URI_PREFIX}movie-1') == []


# ---------------------------------------------------------------------------
# Playback
# ---------------------------------------------------------------------------


def test_play_album_builds_mpd_playlist():
    api = make_api()
    api.get_album_children.return_value = [
        track_item(),
        track_item(Id='track-2', Name='Track Two', IndexNumber=2),
    ]
    mpd = make_mpd()
    backend = make_backend(api, mpd)

    backend.play_album(None, None, content_uri=f'{ALBUM_URI_PREFIX}album-1')

    mpd.clear_playlist.assert_called_once_with()
    mpd.add_to_playlist.assert_has_calls([
        call(STREAM_URL.format(item_id='track-1')),
        call(STREAM_URL.format(item_id='track-2')),
    ])
    mpd.play.assert_called_once_with()
    api.get_album_children.assert_called_once_with('album-1')


def test_play_album_uses_content_uri_over_name_lookup():
    api = make_api()
    api.get_albums.return_value = [album_item()]
    api.get_album_children.return_value = [track_item()]
    mpd = make_mpd()
    backend = make_backend(api, mpd)

    backend.play_album('Artist One', 'Album One',
                       content_uri=f'{ALBUM_URI_PREFIX}album-1')

    api.get_album_children.assert_called_once_with('album-1')


def test_play_album_not_found_logs_and_leaves_mpd_untouched():
    api = make_api()
    api.get_albums.return_value = [album_item()]
    mpd = make_mpd()
    backend = make_backend(api, mpd)

    backend.play_album('Missing', 'No Album')

    mpd.clear_playlist.assert_not_called()
    mpd.play.assert_not_called()


def test_play_single_builds_mpd_playlist():
    api = make_api()
    api.get_item.return_value = track_item()
    mpd = make_mpd()
    backend = make_backend(api, mpd)

    backend.play_single(f'{TRACK_URI_PREFIX}track-1')

    mpd.clear_playlist.assert_called_once_with()
    mpd.add_to_playlist.assert_called_once_with(
        STREAM_URL.format(item_id='track-1'))
    mpd.play.assert_called_once_with()


def test_play_single_sets_stream_to_track_map():
    api = make_api()
    api.get_item.return_value = track_item()
    backend = make_backend(api)

    backend.play_single(f'{TRACK_URI_PREFIX}track-1')

    stream_url = STREAM_URL.format(item_id='track-1')
    assert backend._stream_to_track == {
        stream_url: {
            'uri': f'{TRACK_URI_PREFIX}track-1',
            'title': 'Track One',
            'artist': 'Artist One',
            'album': 'Album One',
            'duration': 12,
            'track': 1,
            'item_id': 'track-1',
            'album_id': 'album-1',
        }
    }


def test_play_single_bad_uri():
    mpd = make_mpd()
    backend = make_backend(mpd=mpd)

    backend.play_single('service:foo:track-1')

    mpd.clear_playlist.assert_not_called()


def test_play_folder_routes_album_uri():
    api = make_api()
    api.get_album_children.return_value = [track_item()]
    mpd = make_mpd()
    backend = make_backend(api, mpd)

    backend.play_folder(f'{ALBUM_URI_PREFIX}album-1')

    mpd.play.assert_called_once_with()
    api.get_album_children.assert_called_once_with('album-1')


def test_play_folder_routes_track_uri():
    api = make_api()
    api.get_item.return_value = track_item()
    mpd = make_mpd()
    backend = make_backend(api, mpd)

    backend.play_folder(f'{TRACK_URI_PREFIX}track-1')

    mpd.add_to_playlist.assert_called_once_with(
        STREAM_URL.format(item_id='track-1'))


def test_play_folder_bad_uri_leaves_mpd_untouched():
    mpd = make_mpd()
    backend = make_backend(mpd=mpd)

    backend.play_folder('service:unknown:value')

    mpd.clear_playlist.assert_not_called()


def test_is_second_swipe_is_false():
    backend = make_backend()

    assert backend.is_second_swipe('anything') is False


def test_playback_failure_does_not_mutate_mpd():
    api = make_api()
    api.get_album_children.side_effect = RuntimeError('offline')
    mpd = make_mpd()
    backend = make_backend(api, mpd)

    backend.play_album(None, None, content_uri=f'{ALBUM_URI_PREFIX}album-1')

    mpd.clear_playlist.assert_not_called()
    mpd.play.assert_not_called()


def test_play_streams_mpd_failure_leaves_mapping_untouched():
    api = make_api()
    api.get_item.return_value = track_item()
    mpd = make_mpd()
    mpd.add_to_playlist.side_effect = RuntimeError('mpd offline')
    backend = make_backend(api, mpd)
    backend._stream_to_track = {'old': 'state'}

    backend.play_single(f'{TRACK_URI_PREFIX}track-1')

    # An MPD failure is logged and the stream->track mapping stays untouched,
    # so a partially built playlist can never masquerade as Jellyfin content.
    assert backend._stream_to_track == {'old': 'state'}


# ---------------------------------------------------------------------------
# Cover art
# ---------------------------------------------------------------------------


def test_get_album_coverart_uses_content_uri(tmp_path):
    api = make_api()
    api.get_albums.return_value = [album_item()]
    backend = make_backend(api)
    backend._cover_cache_dir = tmp_path

    result = backend.get_album_coverart(
        None, None, content_uri=f'{ALBUM_URI_PREFIX}album-1')

    assert result is None  # first call enqueues the download


def test_get_single_coverart(tmp_path):
    api = make_api()
    backend = make_backend(api)
    backend._cover_cache_dir = tmp_path

    assert backend.get_single_coverart(f'{TRACK_URI_PREFIX}track-1') is None
    backend._cover_write_queue.join()

    assert backend.get_single_coverart(
        f'{TRACK_URI_PREFIX}track-1') == 'jellyfin-track-1.jpg'
    api.get_coverart_bytes.assert_called_once_with('track-1')


def test_get_single_coverart_uses_album_cover_for_known_track(tmp_path):
    api = make_api()
    api.get_item.return_value = track_item()
    backend = make_backend(api)
    backend._cover_cache_dir = tmp_path
    backend.play_single(f'{TRACK_URI_PREFIX}track-1')

    assert backend.get_single_coverart(f'{TRACK_URI_PREFIX}track-1') is None
    backend._cover_write_queue.join()

    # A track seen this session resolves to the album cover: one cache file
    # per album instead of one per track.
    assert backend.get_single_coverart(
        f'{TRACK_URI_PREFIX}track-1') == 'jellyfin-album-1.jpg'
    api.get_coverart_bytes.assert_called_once_with('album-1')


def test_status_cover_uses_album_id(tmp_path):
    api = make_api()
    api.get_item.return_value = track_item()
    mpd = make_mpd()
    backend = make_backend(api, mpd)
    backend._cover_cache_dir = tmp_path
    backend.play_single(f'{TRACK_URI_PREFIX}track-1')

    mpd.mpd_status = {
        'file': STREAM_URL.format(item_id='track-1'),
        'state': 'play',
        'song': '0',
    }
    status = backend._normalize_status(mpd.mpd_status)
    assert status['cover_url'] is None  # download enqueued on first poll
    backend._cover_write_queue.join()

    status = backend._normalize_status(mpd.mpd_status)
    assert status['cover_url'] == '/cover-cache/jellyfin-album-1.jpg'
    api.get_coverart_bytes.assert_called_once_with('album-1')


def test_get_single_coverart_resolves_raw_stream_url(tmp_path):
    api = make_api()
    api.get_item.return_value = track_item()
    backend = make_backend(api)
    backend._cover_cache_dir = tmp_path
    (tmp_path / 'jellyfin-album-1.jpg').write_bytes(b'cached-album-cover')

    # A raw stream URL for a track not seen this session resolves through
    # the embedded item id to the already-cached album cover.
    assert backend.get_single_coverart(
        STREAM_URL.format(item_id='track-1')) == 'jellyfin-album-1.jpg'
    api.get_coverart_bytes.assert_not_called()


def test_get_single_coverart_uses_cached_album_cover_for_unmapped_track(tmp_path):
    api = make_api()
    api.get_item.return_value = track_item()
    backend = make_backend(api)
    backend._cover_cache_dir = tmp_path
    (tmp_path / 'jellyfin-album-1.jpg').write_bytes(b'cached-album-cover')

    # No session playback (e.g. after a restart): the album id is resolved
    # from the server once and the already-cached album artwork is reused.
    result = backend.get_single_coverart(f'{TRACK_URI_PREFIX}track-1')

    assert result == 'jellyfin-album-1.jpg'
    api.get_coverart_bytes.assert_not_called()


def test_get_single_coverart_resolves_album_cover_for_unmapped_track(tmp_path):
    api = make_api()
    api.get_item.return_value = track_item()
    backend = make_backend(api)
    backend._cover_cache_dir = tmp_path

    assert backend.get_single_coverart(f'{TRACK_URI_PREFIX}track-1') is None
    backend._cover_write_queue.join()

    # The pending download is the album cover, not a per-track cover.
    assert backend.get_single_coverart(
        f'{TRACK_URI_PREFIX}track-1') == 'jellyfin-album-1.jpg'
    api.get_coverart_bytes.assert_called_once_with('album-1')


def test_get_single_coverart_falls_back_to_track_cover_when_album_unresolvable(tmp_path):
    api = make_api()
    api.get_item.return_value = {}
    backend = make_backend(api)
    backend._cover_cache_dir = tmp_path

    assert backend.get_single_coverart(f'{TRACK_URI_PREFIX}track-1') is None
    backend._cover_write_queue.join()

    # Without an AlbumId the previous per-track fallback stays intact.
    assert backend.get_single_coverart(
        f'{TRACK_URI_PREFIX}track-1') == 'jellyfin-track-1.jpg'
    api.get_coverart_bytes.assert_called_once_with('track-1')


def test_status_cover_resolves_album_for_unmapped_stream(tmp_path):
    api = make_api()
    api.get_item.return_value = track_item()
    mpd = make_mpd()
    backend = make_backend(api, mpd)
    backend._cover_cache_dir = tmp_path
    mpd.mpd_status = {
        'file': STREAM_URL.format(item_id='track-1'),
        'state': 'play',
        'song': '0',
    }

    status = backend._normalize_status(mpd.mpd_status)
    # The stream URL stays masked; the album cover download is enqueued.
    assert status['file'] == ''
    assert status['cover_url'] is None
    backend._cover_write_queue.join()

    status = backend._normalize_status(mpd.mpd_status)
    assert status['cover_url'] == '/cover-cache/jellyfin-album-1.jpg'
    api.get_coverart_bytes.assert_called_once_with('album-1')


def test_status_cover_uses_cached_album_cover_for_unmapped_stream(tmp_path):
    api = make_api()
    api.get_item.return_value = track_item()
    mpd = make_mpd()
    backend = make_backend(api, mpd)
    backend._cover_cache_dir = tmp_path
    (tmp_path / 'jellyfin-album-1.jpg').write_bytes(b'cached-album-cover')
    mpd.mpd_status = {
        'file': STREAM_URL.format(item_id='track-1'),
        'state': 'play',
        'song': '0',
    }

    status = backend._normalize_status(mpd.mpd_status)

    assert status['cover_url'] == '/cover-cache/jellyfin-album-1.jpg'
    api.get_coverart_bytes.assert_not_called()


def test_cover_cache_is_memoized_and_written_async(tmp_path):
    api = make_api()
    backend = make_backend(api)
    backend._cover_cache_dir = tmp_path

    assert backend._cache_coverart('track-1') is None
    backend._cover_write_queue.join()

    assert backend._cache_coverart('track-1') == 'jellyfin-track-1.jpg'
    assert (tmp_path / 'jellyfin-track-1.jpg').exists()
    api.get_coverart_bytes.assert_called_once_with('track-1')


def test_cover_url_is_prefixed(tmp_path):
    api = make_api()
    backend = make_backend(api)
    backend._cover_cache_dir = tmp_path

    assert backend._cover_url('track-1') is None
    backend._cover_write_queue.join()

    assert backend._cover_url('track-1') == '/cover-cache/jellyfin-track-1.jpg'


def test_cover_download_failure_can_be_retried_after_cooldown(tmp_path):
    api = make_api()
    api.get_coverart_bytes.side_effect = [RuntimeError('offline'), b'image']
    backend = make_backend(api)
    backend._cover_cache_dir = tmp_path

    assert backend._cache_coverart('track-1') is None
    backend._cover_write_queue.join()

    # The failed download forgot the pending entry and applied a cooldown:
    # an immediate request must not re-enqueue (no retry storm).
    assert backend._cache_coverart('track-1') is None
    assert backend._cover_write_queue.empty()

    # Once the cooldown has expired the next request triggers the retry.
    backend._cover_retry_after['track-1'] = time.monotonic() - 1.0
    assert backend._cache_coverart('track-1') is None
    backend._cover_write_queue.join()

    assert backend._cache_coverart('track-1') == 'jellyfin-track-1.jpg'
    assert api.get_coverart_bytes.call_count == 2


def test_cover_download_failure_does_not_storm_retries(tmp_path):
    api = make_api()
    api.get_coverart_bytes.side_effect = [RuntimeError('offline')]
    backend = make_backend(api)
    backend._cover_cache_dir = tmp_path

    assert backend._cache_coverart('track-1') is None
    backend._cover_write_queue.join()
    assert api.get_coverart_bytes.call_count == 1

    # Simulate repeated status-poller ticks: none of them may re-enqueue
    # while the cooldown is active.
    for _ in range(20):
        assert backend._cache_coverart('track-1') is None
    assert backend._cover_write_queue.empty()
    assert api.get_coverart_bytes.call_count == 1
    assert 'track-1' in backend._cover_retry_after


def test_cover_reuses_existing_file_after_restart(tmp_path):
    api = make_api()
    backend = make_backend(api)
    backend._cover_cache_dir = tmp_path
    (tmp_path / 'jellyfin-track-1.jpg').write_bytes(b'existing-cover')

    assert backend._cache_coverart('track-1') == 'jellyfin-track-1.jpg'
    api.get_coverart_bytes.assert_not_called()


def test_cover_url_reuses_existing_file_after_restart(tmp_path):
    api = make_api()
    backend = make_backend(api)
    backend._cover_cache_dir = tmp_path
    (tmp_path / 'jellyfin-track-1.jpg').write_bytes(b'existing-cover')

    assert backend._cover_url('track-1') == '/cover-cache/jellyfin-track-1.jpg'
    api.get_coverart_bytes.assert_not_called()


# ---------------------------------------------------------------------------
# Status
# ---------------------------------------------------------------------------


def test_set_active_triggers_immediate_poll(monkeypatch):
    publisher = Mock()
    monkeypatch.setattr(publishing, 'get_publisher', Mock(return_value=publisher))
    mpd = make_mpd()
    mpd.mpd_status = {'state': 'stop'}
    backend = make_backend(mpd=mpd)
    backend.set_active(True)

    publisher.send.assert_called_once_with(
        'playerstatus',
        {
            'state': 'stop',
            'songid': None,
            'song': '',
            'elapsed': '0.0',
            'random': '0',
            'repeat': '0',
            'single': '0',
            'title': '',
            'artist': '',
            'album': '',
            'duration': '0',
            'file': None,
            'provider': 'jellyfin',
            'cover_url': None,
        },
    )

    publisher.reset_mock()
    backend.set_active(False)
    backend._publish_status()
    publisher.send.assert_not_called()


def test_publish_status_catches_errors(monkeypatch):
    publisher = Mock()
    monkeypatch.setattr(publishing, 'get_publisher', Mock(return_value=publisher))
    mpd = make_mpd()
    mpd.mpd_status = {'state': 'play'}
    backend = make_backend(mpd=mpd)
    backend._active = True
    # Force _normalize_status to raise inside _publish_status.
    backend._cover_url = Mock(side_effect=RuntimeError('boom'))

    backend._publish_status()

    # The exception is caught (the timer worker must survive) and nothing
    # is published.
    publisher.send.assert_not_called()


def test_status_publish_is_normalized_for_album_and_single(monkeypatch):
    publisher = Mock()
    monkeypatch.setattr(publishing, 'get_publisher', Mock(return_value=publisher))
    api = make_api()
    api.get_album_children.return_value = [track_item()]
    api.get_item.return_value = track_item()
    mpd = make_mpd()
    backend = make_backend(api, mpd)

    for playback in ('album', 'single'):
        backend._stream_to_track = {}
        if playback == 'album':
            backend.play_album(None, None, content_uri=f'{ALBUM_URI_PREFIX}album-1')
        else:
            backend.play_single(f'{TRACK_URI_PREFIX}track-1')
        backend._active = True
        mpd.mpd_status = {'file': STREAM_URL.format(item_id='track-1'),
                          'state': 'play', 'song': '0', 'elapsed': '1.5'}
        publisher.reset_mock()
        backend._publish_status()

        sent = publisher.send.call_args[0][1]
        assert sent['provider'] == 'jellyfin'
        assert sent['file'] == f'{TRACK_URI_PREFIX}track-1'
        assert sent['title'] == 'Track One'
        assert sent['artist'] == 'Artist One'
        assert sent['album'] == 'Album One'
        assert sent['duration'] == '12'
        assert sent['state'] == 'play'


def test_playerstatus_masks_stream_url():
    api = make_api()
    api.get_item.return_value = track_item()
    mpd = make_mpd()
    mpd.playerstatus.return_value = {
        'file': STREAM_URL.format(item_id='track-1'),
        'state': 'play',
    }
    backend = make_backend(api, mpd)
    backend.play_single(f'{TRACK_URI_PREFIX}track-1')

    status = backend.playerstatus()

    assert status['file'] == f'{TRACK_URI_PREFIX}track-1'
    assert 'api_key' not in str(status)


def test_playerstatus_resolves_normalized_stream_url_via_item_id():
    api = make_api()
    api.get_item.return_value = track_item()
    mpd = make_mpd()
    backend = make_backend(api, mpd)
    backend.play_single(f'{TRACK_URI_PREFIX}track-1')

    # MPD reports a normalized variant of the stream URL (e.g. an extra query
    # parameter), so the exact map lookup misses and the item id is used.
    mpd.playerstatus.return_value = {
        'file': STREAM_URL.format(item_id='track-1') + '&param=1',
        'state': 'play',
        'song': '0',
    }

    status = backend.playerstatus()

    assert status['file'] == f'{TRACK_URI_PREFIX}track-1'
    assert status['title'] == 'Track One'
    assert 'api_key' not in str(status)


def test_playerstatus_masks_unmapped_stream_url():
    api = make_api()
    mpd = make_mpd()
    backend = make_backend(api, mpd)
    mpd.playerstatus.return_value = {
        'file': 'http://jellyfin.local:8096/Audio/unknown-item/stream?static=true&api_key=secret',
        'state': 'play',
    }

    status = backend.playerstatus()

    # The raw stream URL (with API key) must never surface on an RPC channel.
    assert status['file'] == ''
    assert 'api_key' not in str(status)
    assert 'secret' not in str(status)


def test_playerstatus_keeps_non_stream_mpd_file():
    api = make_api()
    mpd = make_mpd()
    backend = make_backend(api, mpd)
    mpd.playerstatus.return_value = {
        'file': '/home/pi/Music/SomeAlbum/track.mp3',
        'state': 'play',
    }

    status = backend.playerstatus()

    # A plain MPD file carries no credentials and stays visible.
    assert status['file'] == '/home/pi/Music/SomeAlbum/track.mp3'


def test_playlistinfo_returns_single_normalized_status():
    api = make_api()
    api.get_item.return_value = track_item()
    mpd = make_mpd()
    mpd.playerstatus.return_value = {
        'file': STREAM_URL.format(item_id='track-1'),
        'state': 'play',
    }
    backend = make_backend(api, mpd)
    backend.play_single(f'{TRACK_URI_PREFIX}track-1')

    result = backend.playlistinfo()

    assert len(result) == 1
    assert result[0]['file'] == f'{TRACK_URI_PREFIX}track-1'
    assert result[0]['provider'] == 'jellyfin'


def test_get_current_song_with_param():
    api = make_api()
    api.get_item.return_value = track_item()
    mpd = make_mpd()
    mpd.playerstatus.return_value = {'file': STREAM_URL.format(item_id='track-1')}
    backend = make_backend(api, mpd)
    backend.play_single(f'{TRACK_URI_PREFIX}track-1')

    assert backend.get_current_song('title') == 'Track One'


# ---------------------------------------------------------------------------
# Active-backend delegation
# ---------------------------------------------------------------------------


def test_transport_controls_delegate_to_mpd():
    mpd = make_mpd()
    backend = make_backend(mpd=mpd)

    backend.stop()
    backend.play()
    backend.pause(0)
    backend.next()
    backend.prev()
    backend.seek(12)
    backend.rewind()
    backend.toggle()
    backend.shuffle('enable')
    backend.repeat('disable')
    backend.get_volume()
    backend.set_volume(33)
    backend.get_player_type_and_version()

    mpd.stop.assert_called_once_with()
    mpd.play.assert_called_once_with()
    mpd.pause.assert_called_once_with(0)
    mpd.next.assert_called_once_with()
    mpd.prev.assert_called_once_with()
    mpd.seek.assert_called_once_with(12)
    mpd.rewind.assert_called_once_with()
    mpd.toggle.assert_called_once_with()
    mpd.shuffle.assert_called_once_with('enable')
    mpd.repeat.assert_called_once_with('disable')
    mpd.get_volume.assert_called_once_with()
    mpd.set_volume.assert_called_once_with(33)
    mpd.get_player_type_and_version.assert_called_once_with()


def test_replay_restarts_current_track():
    mpd = make_mpd()
    backend = make_backend(mpd=mpd)

    backend.replay()

    mpd.seek.assert_called_once_with(0)
    mpd.play.assert_called_once_with()


def test_replay_if_stopped_rewinds_when_stopped():
    mpd = make_mpd()
    mpd.mpd_status = {'state': 'stop'}
    backend = make_backend(mpd=mpd)

    backend.replay_if_stopped()

    mpd.rewind.assert_called_once_with()


def test_replay_if_stopped_is_noop_while_playing():
    mpd = make_mpd()
    mpd.mpd_status = {'state': 'play'}
    backend = make_backend(mpd=mpd)

    backend.replay_if_stopped()

    mpd.rewind.assert_not_called()


def test_resume_seeks_to_saved_position_and_plays():
    mpd = make_mpd()
    mpd.mpd_status = {'song': 2, 'elapsed': '14.5'}
    backend = make_backend(mpd=mpd)

    backend.resume()

    mpd.mpd_client.seek.assert_called_once_with(2, '14.5')
    mpd.mpd_client.play.assert_called_once_with()


def test_exit_closes_session_and_timer():
    api = make_api()
    backend = make_backend(api)
    timer = backend._status_timer

    backend.exit()

    api.close.assert_called_once_with()
    assert timer.closed is True
    assert backend._api is None


# ---------------------------------------------------------------------------
# URI helpers
# ---------------------------------------------------------------------------


def test_component_id_from_uri_with_prefix():
    assert component_id_from_uri(f'{TRACK_URI_PREFIX}track-1',
                                 prefix=TRACK_URI_PREFIX) == 'track-1'
    assert component_id_from_uri(f'{ALBUM_URI_PREFIX}album-1',
                                 prefix=TRACK_URI_PREFIX) is None
    assert component_id_from_uri('not-a-uri', prefix=TRACK_URI_PREFIX) is None


def test_component_id_from_uri_without_prefix():
    assert component_id_from_uri(f'{ALBUM_URI_PREFIX}album-1') == 'album-1'
    assert component_id_from_uri(f'{TRACK_URI_PREFIX}track-1') == 'track-1'
    assert component_id_from_uri('service:other:value') is None
    assert component_id_from_uri(None) is None


# ---------------------------------------------------------------------------
# configure_jellyfin
# ---------------------------------------------------------------------------


def make_player_ctrl():
    return SimpleNamespace(
        _get_backend=Mock(return_value=make_mpd()),
        register_backend=Mock(),
    )


def test_configure_jellyfin_disabled(monkeypatch):
    reset_cfg()
    player_ctrl = make_player_ctrl()

    assert configure_jellyfin(player_ctrl) is None
    player_ctrl.register_backend.assert_not_called()


def test_configure_jellyfin_missing_config(monkeypatch):
    cfg = reset_cfg()
    cfg.setn('players', 'jellyfin', 'enabled', value=True)
    player_ctrl = make_player_ctrl()

    assert configure_jellyfin(player_ctrl) is None
    player_ctrl.register_backend.assert_not_called()


def test_configure_jellyfin_registers(monkeypatch):
    monkeypatch.setattr(
        'jukebox.multitimer.GenericEndlessTimerClass', FakeTimer)
    cfg = reset_cfg()
    cfg.setn('players', 'jellyfin', 'enabled', value=True)
    cfg.setn('players', 'jellyfin', 'host', value='http://jellyfin.local:8096')
    cfg.setn('players', 'jellyfin', 'api_key', value='secret')
    player_ctrl = make_player_ctrl()

    backend = configure_jellyfin(player_ctrl)

    assert backend is not None
    player_ctrl.register_backend.assert_called_once_with('jellyfin', backend)


def test_configure_jellyfin_uses_login_credentials(monkeypatch):
    monkeypatch.setattr(
        'jukebox.multitimer.GenericEndlessTimerClass', FakeTimer)
    cfg = reset_cfg()
    cfg.setn('players', 'jellyfin', 'enabled', value=True)
    cfg.setn('players', 'jellyfin', 'host', value='http://jellyfin.local:8096')
    cfg.setn('players', 'jellyfin', 'username', value='user')
    cfg.setn('players', 'jellyfin', 'password', value='pass')
    player_ctrl = make_player_ctrl()

    backend = configure_jellyfin(player_ctrl)

    assert backend is not None
    assert backend._api.username == 'user'
    assert backend._api.password == 'pass'
    assert backend._api.api_key == ''


def test_configure_jellyfin_requires_credentials(monkeypatch):
    cfg = reset_cfg()
    cfg.setn('players', 'jellyfin', 'enabled', value=True)
    cfg.setn('players', 'jellyfin', 'host', value='http://jellyfin.local:8096')
    player_ctrl = make_player_ctrl()

    assert configure_jellyfin(player_ctrl) is None
    player_ctrl.register_backend.assert_not_called()


def test_configure_jellyfin_reads_cache_ttl():
    reset_cfg()

    cache_ttl = cfghandler.get_handler('jukebox').setndefault(
        'players', 'jellyfin', 'catalog_cache_ttl', value=120)

    assert cache_ttl == 120


def test_configure_jellyfin_default_cache_ttl():
    reset_cfg()

    cache_ttl = cfghandler.get_handler('jukebox').setndefault(
        'players', 'jellyfin', 'catalog_cache_ttl', value=300)

    assert cache_ttl == 300


def test_configure_jellyfin_does_not_authenticate_at_startup(monkeypatch):
    monkeypatch.setattr(
        'jukebox.multitimer.GenericEndlessTimerClass', FakeTimer)
    api = make_api()
    monkeypatch.setattr('components.jellyfin.JellyfinApiClient', Mock(return_value=api))
    cfg = reset_cfg()
    cfg.setn('players', 'jellyfin', 'enabled', value=True)
    cfg.setn('players', 'jellyfin', 'host', value='http://jellyfin.local:8096')
    cfg.setn('players', 'jellyfin', 'api_key', value='secret')
    player_ctrl = make_player_ctrl()

    backend = configure_jellyfin(player_ctrl)

    assert backend._api is api
    api.authenticate.assert_not_called()


def test_configure_jellyfin_starts_catalog_warmup(monkeypatch):
    monkeypatch.setattr(
        'jukebox.multitimer.GenericEndlessTimerClass', FakeTimer)
    api = make_api()
    api.get_albums.return_value = [album_item()]
    monkeypatch.setattr('components.jellyfin.JellyfinApiClient', Mock(return_value=api))
    cfg = reset_cfg()
    cfg.setn('players', 'jellyfin', 'enabled', value=True)
    cfg.setn('players', 'jellyfin', 'host', value='http://jellyfin.local:8096')
    cfg.setn('players', 'jellyfin', 'api_key', value='secret')
    player_ctrl = make_player_ctrl()

    backend = configure_jellyfin(player_ctrl)

    assert backend._warmup_started is True
    deadline = time.monotonic() + 2.0
    while backend._catalog_cache is None and time.monotonic() < deadline:
        time.sleep(0.01)

    assert backend._catalog_cache == [album_item()]


def test_configure_jellyfin_reads_request_timeout(monkeypatch):
    monkeypatch.setattr(
        'jukebox.multitimer.GenericEndlessTimerClass', FakeTimer)
    cfg = reset_cfg()
    cfg.setn('players', 'jellyfin', 'enabled', value=True)
    cfg.setn('players', 'jellyfin', 'host', value='http://jellyfin.local:8096')
    cfg.setn('players', 'jellyfin', 'api_key', value='secret')
    cfg.setn('players', 'jellyfin', 'request_timeout', value=45)
    player_ctrl = make_player_ctrl()

    backend = configure_jellyfin(player_ctrl)

    assert backend._api.timeout == 45


def test_configure_jellyfin_default_request_timeout():
    reset_cfg()

    timeout = cfghandler.get_handler('jukebox').setndefault(
        'players', 'jellyfin', 'request_timeout', value=30)

    assert timeout == 30


def test_configure_jellyfin_invalid_cache_ttl_falls_back(monkeypatch):
    monkeypatch.setattr('jukebox.multitimer.GenericEndlessTimerClass', FakeTimer)
    cfg = reset_cfg()
    cfg.setn('players', 'jellyfin', 'enabled', value=True)
    cfg.setn('players', 'jellyfin', 'host', value='http://jellyfin.local:8096')
    cfg.setn('players', 'jellyfin', 'api_key', value='secret')
    cfg.setn('players', 'jellyfin', 'catalog_cache_ttl', value='not-a-number')
    player_ctrl = make_player_ctrl()

    backend = configure_jellyfin(player_ctrl)

    assert backend is not None
    assert backend._cache_ttl == 300.0


def test_configure_jellyfin_nonpositive_cache_ttl_falls_back(monkeypatch):
    monkeypatch.setattr('jukebox.multitimer.GenericEndlessTimerClass', FakeTimer)
    cfg = reset_cfg()
    cfg.setn('players', 'jellyfin', 'enabled', value=True)
    cfg.setn('players', 'jellyfin', 'host', value='http://jellyfin.local:8096')
    cfg.setn('players', 'jellyfin', 'api_key', value='secret')
    cfg.setn('players', 'jellyfin', 'catalog_cache_ttl', value=-5)
    player_ctrl = make_player_ctrl()

    backend = configure_jellyfin(player_ctrl)

    assert backend is not None
    assert backend._cache_ttl == 300.0


def test_configure_jellyfin_invalid_request_timeout_falls_back(monkeypatch):
    monkeypatch.setattr('jukebox.multitimer.GenericEndlessTimerClass', FakeTimer)
    cfg = reset_cfg()
    cfg.setn('players', 'jellyfin', 'enabled', value=True)
    cfg.setn('players', 'jellyfin', 'host', value='http://jellyfin.local:8096')
    cfg.setn('players', 'jellyfin', 'api_key', value='secret')
    cfg.setn('players', 'jellyfin', 'request_timeout', value='abc')
    player_ctrl = make_player_ctrl()

    backend = configure_jellyfin(player_ctrl)

    assert backend is not None
    assert backend._api.timeout == DEFAULT_TIMEOUT
