import {
  afterEach,
  beforeEach,
  describe,
  expect,
  test,
  vi,
} from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';

import AppSettingsContext from '../../context/appsettings/context';
import PlayerContext from '../../context/player/context';
import request from '../../utils/request';
import Player from './index';

vi.mock('../../utils/request', () => ({
  default: vi.fn(),
}));

vi.mock('react-i18next', () => ({
  useTranslation: () => ({
    t: (key) => key,
  }),
}));

// The transport sub-components are not part of the Jellyfin cover flow and
// would otherwise trigger unrelated RPC requests (e.g. getVolume).
vi.mock('./controls', () => ({ default: () => null }));
vi.mock('./display', () => ({ default: () => null }));
vi.mock('./seekbar', () => ({ default: () => null }));
vi.mock('./volume', () => ({ default: () => null }));

const renderPlayer = (playerstatus) => render(
  <AppSettingsContext.Provider value={{ settings: { show_covers: true } }}>
    <PlayerContext.Provider value={{ state: { playerstatus }, setState: vi.fn() }}>
      <Player />
    </PlayerContext.Provider>
  </AppSettingsContext.Provider>,
);

describe('Player with a Jellyfin status', () => {
  beforeEach(() => {
    request.mockReset();
    request.mockResolvedValue({ result: null, error: null });
  });

  afterEach(() => {
    vi.clearAllMocks();
  });

  test('uses the prefixed cover_url verbatim without a getSingleCoverArt round-trip', async () => {
    renderPlayer({
      provider: 'jellyfin',
      file: 'service:jellyfin:track:track-1',
      cover_url: '/cover-cache/jellyfin-track-1.jpg',
    });

    const cover = await screen.findByRole('img', { name: 'player.cover.title' });
    expect(cover).toHaveAttribute('src', '/cover-cache/jellyfin-track-1.jpg');
    expect(request).not.toHaveBeenCalledWith(
      'getSingleCoverArt',
      expect.anything(),
    );
  });

  test('fetches the cover through getSingleCoverArt and prefixes the returned filename', async () => {
    request.mockImplementation(async (command) => {
      if (command === 'getSingleCoverArt') {
        return { result: 'jellyfin-track-1.jpg', error: null };
      }
      return { result: null, error: null };
    });
    renderPlayer({
      provider: 'jellyfin',
      file: 'service:jellyfin:track:track-1',
      cover_url: null,
    });

    expect(request).toHaveBeenCalledWith('getSingleCoverArt', {
      song_url: 'service:jellyfin:track:track-1',
      provider: 'jellyfin',
    });
    await waitFor(() => {
      expect(screen.getByRole('img', { name: 'player.cover.title' }))
        .toHaveAttribute('src', '/cover-cache/jellyfin-track-1.jpg');
    });
  });
});
