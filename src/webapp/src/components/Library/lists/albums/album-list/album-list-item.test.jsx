import {
  afterEach,
  beforeEach,
  describe,
  expect,
  test,
  vi,
} from 'vitest';
import { act, render, screen, waitFor } from '@testing-library/react';

import AppSettingsContext from '../../../../../context/appsettings/context';
import request from '../../../../../utils/request';
import AlbumListItem from './album-list-item';

vi.mock('../../../../../utils/request', () => ({
  default: vi.fn(),
}));

vi.mock('react-router-dom', () => ({
  Link: ({ to, children }) => <a href={to}>{children}</a>,
  useLocation: () => ({ search: '' }),
}));

vi.mock('react-i18next', () => ({
  useTranslation: () => ({
    t: (key, options = {}) => options.defaultValue || key,
  }),
}));

const jellyfinAlbum = {
  albumartist: 'Artist One',
  album: 'Album One',
  content_type: 'album',
  content_uri: 'service:jellyfin:album:album-1',
  cover_url: null,
  provider: 'jellyfin',
};

const renderItem = (props = {}) => render(
  <AppSettingsContext.Provider value={{ settings: { show_covers: true } }}>
    <AlbumListItem {...jellyfinAlbum} {...props} />
  </AppSettingsContext.Provider>,
);

describe('AlbumListItem cover resolution', () => {
  beforeEach(() => {
    request.mockReset();
    request.mockResolvedValue({ result: null, error: null });
  });

  afterEach(() => {
    vi.clearAllMocks();
    vi.useRealTimers();
  });

  test('uses a provided cover_url without a getAlbumCoverArt round-trip', () => {
    renderItem({ cover_url: '/cover-cache/jellyfin-album-1.jpg' });

    expect(screen.getByRole('img', { name: 'Cover' }))
      .toHaveAttribute('src', '/cover-cache/jellyfin-album-1.jpg');
    expect(request).not.toHaveBeenCalled();
  });

  test('fetches a missing cover through getAlbumCoverArt', async () => {
    request.mockResolvedValue({ result: 'jellyfin-album-1.jpg', error: null });
    renderItem();

    expect(request).toHaveBeenCalledWith('getAlbumCoverArt', {
      albumartist: 'Artist One',
      album: 'Album One',
      content_uri: 'service:jellyfin:album:album-1',
      provider: 'jellyfin',
    });
    await waitFor(() => {
      expect(screen.getByRole('img', { name: 'Cover' }))
        .toHaveAttribute('src', '/cover-cache/jellyfin-album-1.jpg');
    });
  });

  test('re-checks a CACHE_PENDING cover until the cache file is ready', async () => {
    vi.useFakeTimers();
    let calls = 0;
    request.mockImplementation(async (command) => {
      if (command === 'getAlbumCoverArt') {
        calls += 1;
        return { result: calls === 1 ? 'CACHE_PENDING' : 'jellyfin-album-1.jpg', error: null };
      }
      return { result: null, error: null };
    });
    renderItem();

    // First attempt reported CACHE_PENDING: the placeholder stays.
    await act(async () => {});
    expect(screen.getByRole('img', { name: 'Cover' })).not.toHaveAttribute(
      'src', '/cover-cache/jellyfin-album-1.jpg');

    // The re-check resolves the now-cached cover without a re-mount.
    await act(async () => {
      vi.advanceTimersByTime(1000);
    });
    expect(screen.getByRole('img', { name: 'Cover' }))
      .toHaveAttribute('src', '/cover-cache/jellyfin-album-1.jpg');
    expect(calls).toBe(2);
  });

  test('re-checks a Jellyfin pending cover (null result) once downloaded', async () => {
    vi.useFakeTimers();
    let calls = 0;
    request.mockImplementation(async () => {
      calls += 1;
      return { result: calls === 1 ? null : 'jellyfin-album-1.jpg', error: null };
    });
    renderItem();

    await act(async () => {});
    await act(async () => {
      vi.advanceTimersByTime(1000);
    });
    expect(screen.getByRole('img', { name: 'Cover' }))
      .toHaveAttribute('src', '/cover-cache/jellyfin-album-1.jpg');
    expect(calls).toBe(2);
  });

  test('stops re-checking after the retry limit', async () => {
    vi.useFakeTimers();
    request.mockResolvedValue({ result: 'CACHE_PENDING', error: null });
    renderItem();

    await act(async () => {});
    // Attempts are scheduled at +1s, +2s and +3s -> four calls in total.
    for (const delay of [1000, 2000, 3000]) {
      await act(async () => {
        vi.advanceTimersByTime(delay);
      });
    }
    expect(request).toHaveBeenCalledTimes(4);
    await act(async () => {
      vi.advanceTimersByTime(10000);
    });
    expect(request).toHaveBeenCalledTimes(4);
  });
});
