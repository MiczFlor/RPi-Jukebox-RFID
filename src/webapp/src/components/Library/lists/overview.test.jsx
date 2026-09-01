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

import AppSettingsContext from '../../../context/appsettings/context';
import request from '../../../utils/request';
import LibraryOverview from './overview';

vi.mock('../../../utils/request', () => ({
  default: vi.fn(),
}));

vi.mock('react-i18next', () => ({
  useTranslation: () => ({
    t: (key, options = {}) => {
      const labels = {
        'library.sources.jellyfin': 'Jellyfin',
        'library.sources.mpd': 'Local',
        'library.header.albums': 'Albums',
        'library.overview.group': `${options.source} ${options.view}`,
        'library.overview.show-all': 'Show all',
        'library.albums.no-music': 'no music',
        'library.albums.empty-library': 'empty library',
      };
      return labels[key] || options.defaultValue || key;
    },
  }),
}));

const sources = [
  {
    id: 'jellyfin',
    label: 'Jellyfin',
    views: [
      { id: 'albums', label: 'Albums', kind: 'items', content_types: ['album'] },
    ],
  },
  {
    id: 'mpd',
    label: 'Local',
    views: [
      { id: 'albums', label: 'Albums', kind: 'items', content_types: ['album'] },
      { id: 'folders', label: 'Folders', kind: 'folders', content_types: [] },
    ],
  },
];

const catalogItems = [
  {
    provider: 'jellyfin',
    content_type: 'album',
    content_uri: 'service:jellyfin:album:album-1',
    albumartist: 'Artist One',
    album: 'Album One',
    cover_url: null,
  },
  {
    provider: 'mpd',
    content_type: 'album',
    content_uri: 'mpd:album:1',
    albumartist: 'Local Artist',
    album: 'Local Album',
    cover_url: null,
  },
];

const renderOverview = () => render(
  <MemoryRouter>
    <AppSettingsContext.Provider value={{ settings: { show_covers: false } }}>
      <LibraryOverview musicFilter="" sources={sources} />
    </AppSettingsContext.Provider>
  </MemoryRouter>,
);

describe('Library overview with a Jellyfin source', () => {
  beforeEach(() => {
    request.mockReset();
    request.mockResolvedValue({ result: catalogItems, error: null });
  });

  afterEach(() => {
    vi.clearAllMocks();
  });

  test('groups Jellyfin albums into their own source section', async () => {
    renderOverview();

    expect(await screen.findByText('Jellyfin Albums')).toBeInTheDocument();
    expect(screen.getByText('Local Albums')).toBeInTheDocument();
    expect(screen.getByText('Album One')).toBeInTheDocument();
    expect(screen.getByText('Local Album')).toBeInTheDocument();
  });

  test('links the Jellyfin group to the albums source view', async () => {
    renderOverview();

    const showAllLinks = await screen.findAllByRole('link', { name: 'Show all' });
    const hrefs = showAllLinks.map((link) => link.getAttribute('href'));
    expect(hrefs).toContain('/library/jellyfin/albums');
    expect(hrefs).toContain('/library/mpd/albums');
  });

  test('skips folder views when grouping sources', async () => {
    renderOverview();

    expect(await screen.findByText('Jellyfin Albums')).toBeInTheDocument();
    expect(screen.queryByText('Folders')).not.toBeInTheDocument();
  });
});
