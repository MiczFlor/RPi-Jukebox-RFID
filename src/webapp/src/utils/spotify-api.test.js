import {
  afterEach,
  beforeEach,
  expect,
  test,
  vi,
} from 'vitest';

import {
  addSpotifyLibraryItem,
  disconnectSpotify,
  getSpotifyLibrary,
  getSpotifyStatus,
  removeSpotifyLibraryItem,
  removeSpotifyLibraryItems,
  setSpotifyLibraryMode,
  startSpotifyAuthorization,
} from './spotify-api';


const response = (body, options = {}) => ({
  json: vi.fn().mockResolvedValue(body),
  ok: options.ok ?? true,
  status: options.status ?? 200,
});

beforeEach(() => {
  global.fetch = vi.fn();
});

afterEach(() => {
  delete global.fetch;
});

test('loads status, starts PKCE authorization, and disconnects', async () => {
  fetch
    .mockResolvedValueOnce(response({ connected: false }))
    .mockResolvedValueOnce(response({ authorization_url: 'https://accounts.test' }))
    .mockResolvedValueOnce(response(null, { status: 204 }));

  await expect(getSpotifyStatus()).resolves.toEqual({ connected: false });
  await expect(startSpotifyAuthorization()).resolves.toEqual({
    authorization_url: 'https://accounts.test',
  });
  await expect(disconnectSpotify()).resolves.toEqual({});

  expect(fetch.mock.calls).toEqual([
    ['/api/v1/spotify', {}],
    ['/api/v1/spotify/oauth/start', { method: 'POST' }],
    ['/api/v1/spotify', { method: 'DELETE' }],
  ]);
});

test('loads and updates the curated Spotify library', async () => {
  fetch
    .mockResolvedValueOnce(response({ mode: 'account', items: [] }))
    .mockResolvedValueOnce(response({ mode: 'curated', items: [] }))
    .mockResolvedValueOnce(response({ item: { content_uri: 'spotify:album:1' } }))
    .mockResolvedValueOnce(response({ mode: 'curated', items: [] }))
    .mockResolvedValueOnce(response({ mode: 'curated', items: [] }));

  await getSpotifyLibrary();
  await setSpotifyLibraryMode('curated');
  await addSpotifyLibraryItem('https://open.spotify.com/album/1');
  await removeSpotifyLibraryItem('spotify:album:1');
  await removeSpotifyLibraryItems([
    'spotify:album:1',
    'spotify:playlist:2',
  ]);

  expect(fetch.mock.calls).toEqual([
    ['/api/v1/spotify/library', {}],
    ['/api/v1/spotify/library', {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ mode: 'curated' }),
    }],
    ['/api/v1/spotify/library/items', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        link: 'https://open.spotify.com/album/1',
      }),
    }],
    ['/api/v1/spotify/library/items', {
      method: 'DELETE',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ uri: 'spotify:album:1' }),
    }],
    ['/api/v1/spotify/library/items', {
      method: 'DELETE',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        uris: ['spotify:album:1', 'spotify:playlist:2'],
      }),
    }],
  ]);
});

test('returns structured Spotify API errors', async () => {
  fetch.mockResolvedValue(response(
    { error: { code: 'spotify_not_configured', message: 'Configure it.' } },
    { ok: false, status: 400 },
  ));

  await expect(startSpotifyAuthorization()).rejects.toMatchObject({
    code: 'spotify_not_configured',
    message: 'Configure it.',
    status: 400,
  });
});
