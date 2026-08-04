# Player Backends

The player package exposes one stable RPC and RFID-card contract while routing
content to one of several playback backends. The first registered backend is
the default for legacy calls that do not include a provider.

## Register A Backend

Create the backend during player initialization and register it with a stable,
lowercase identifier:

```python
coordinator.register_backend('streaming', backend)
```

Passing `make_active=True` selects the backend immediately. Normal content
playback selects a backend from the request's `provider`; switching stops the
previous backend first.

A backend may implement `set_active(active)`. The coordinator calls it whenever
selection changes so polling backends can publish `playerstatus` only while
active. Status payloads must include the backend identifier as `provider`.

## Playback Contract

Provider-aware calls keep the existing command names:

```python
play_single(song_url, provider=None)
play_album(albumartist, album, content_uri=None, provider=None)
```

Cover lookup and catalog-detail calls accept the same provider metadata.
Calls without `provider` route to the default backend, preserving existing
RFID cards and local paths. Provider integrations must therefore store their
identifier alongside the stable content URI when creating a card action.

Folder playback, folder browsing, local library updates, and cover-cache
flushing route to the default backend. Transport controls such as pause, next,
seek, and volume continue to target the active backend.

## Library Contract

Each catalog backend describes its Web App navigation through
`library_source()`:

```python
{
    'id': 'streaming',
    'label': 'Streaming',
    'views': [
        {
            'id': 'playlists',
            'label': 'Playlists',
            'kind': 'items',
            'content_types': ['playlist'],
        },
    ],
}
```

Use `kind: items` for catalog lists rendered with the shared item and track
views. The built-in local backend also uses `kind: folders` for file
management.

Implement `list_library_items(content_types=None)` and return entries in this
shape:

```python
{
    'provider': 'streaming',
    'content_type': 'playlist',
    'content_uri': 'service:playlist:stable-id',
    'albumartist': 'Owner or artist',
    'album': 'Display title',
    'cover_url': 'https://example.test/cover.jpg',
}
```

`content_uri` must remain stable because playback and RFID assignments retain
it. `cover_url` may be `None`; cover lookup can instead return either a remote
URL or a filename from the local cover cache.

The coordinator combines available sources and items for the overview while
isolating failures from optional catalogs. A request for one explicit provider
returns that provider's error to the caller.

## Compatibility

The legacy `list_albums`, album/song lookup, and playback commands remain
available. Local album and song results now carry provider metadata, while
older clients can ignore the additional fields. Existing library URLs are
redirected to the source-aware routes.
