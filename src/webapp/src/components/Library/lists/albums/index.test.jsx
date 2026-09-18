import {
  afterEach,
  beforeEach,
  describe,
  expect,
  test,
  vi,
} from 'vitest';
import { render, screen } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';

import AppSettingsContext from '../../../../context/appsettings/context';
import request from '../../../../utils/request';
import Albums from './index';

vi.mock('../../../../utils/request', () => ({
  default: vi.fn(),
}));

vi.mock('react-i18next', () => ({
  useTranslation: () => ({
    t: (key, options = {}) => options.defaultValue || key,
  }),
}));

const jellyfinAlbums = [
  {
    provider: 'jellyfin',
    content_type: 'album',
    content_uri: 'service:jellyfin:album:album-1',
    albumartist: 'Artist One',
    album: 'Album One',
    cover_url: null,
  },
  {
    provider: 'jellyfin',
    content_type: 'album',
    content_uri: 'service:jellyfin:album:album-2',
    albumartist: 'Artist Two',
    album: 'Album Two',
    cover_url: null,
  },
];

const renderAlbums = (props = {}) => render(
  <MemoryRouter>
    <AppSettingsContext.Provider value={{ settings: { show_covers: true } }}>
      <Albums
        contentTypes={['album']}
        isSelecting={false}
        musicFilter=""
        provider="jellyfin"
        view="albums"
        {...props}
      />
    </AppSettingsContext.Provider>
  </MemoryRouter>,
);

describe('Jellyfin album library view', () => {
  beforeEach(() => {
    request.mockReset();
    request.mockImplementation(async (command) => {
      if (command === 'libraryItems') {
        return { result: jellyfinAlbums, error: null };
      }
      return { result: null, error: null };
    });
  });

  afterEach(() => {
    vi.clearAllMocks();
  });

  test('fetches the album catalog with the jellyfin provider and album content type', async () => {
    renderAlbums();

    expect(await screen.findByText('Album One')).toBeInTheDocument();
    expect(request).toHaveBeenCalledWith('libraryItems', {
      provider: 'jellyfin',
      content_types: ['album'],
    });
  });

  test('renders Jellyfin album titles and artists from the catalog', async () => {
    renderAlbums();

    expect(await screen.findByText('Album One')).toBeInTheDocument();
    expect(screen.getByText('Album Two')).toBeInTheDocument();
    expect(screen.getByText('Artist One')).toBeInTheDocument();
    expect(screen.getByText('Artist Two')).toBeInTheDocument();
  });

  test('requests cover art through the jellyfin provider', async () => {
    renderAlbums();

    await screen.findByText('Album One');
    expect(request).toHaveBeenCalledWith('getAlbumCoverArt', {
      albumartist: 'Artist One',
      album: 'Album One',
      content_uri: 'service:jellyfin:album:album-1',
      provider: 'jellyfin',
    });
  });

  test('shows the loading-error state when the catalog request fails', async () => {
    request.mockResolvedValue({ result: null, error: new Error('offline') });
    renderAlbums();

    expect(await screen.findByText('library.loading-error')).toBeInTheDocument();
    expect(screen.queryByText('Album One')).not.toBeInTheDocument();
  });
});
