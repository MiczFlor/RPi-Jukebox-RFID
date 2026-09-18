import {
  afterEach,
  beforeEach,
  describe,
  expect,
  test,
  vi,
} from 'vitest';
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { MemoryRouter, Route, Routes } from 'react-router-dom';

import request from '../../../../../utils/request';
import SongList from './index';
import SongListControls from './song-list-controls';
import SongListItem from './song-list-item';

vi.mock('../../../../../utils/request', () => ({
  default: vi.fn(),
}));

vi.mock('react-i18next', () => ({
  useTranslation: () => ({
    t: (key, options = {}) => {
      const labels = { 'library.albums.assign-to-card': 'assign-to-card' };
      return labels[key] || options.defaultValue || key;
    },
  }),
}));

const jellyfinSongs = [
  {
    provider: 'jellyfin',
    album: 'Album One',
    artist: 'Artist One',
    title: 'Track One',
    file: 'service:jellyfin:track:track-1',
    track: 1,
    duration: 12,
    cover_url: null,
  },
];

const renderSongList = () => render(
  <MemoryRouter
    initialEntries={[
      '/library/jellyfin/albums/Artist%20One/Album%20One?content_uri=service%3Ajellyfin%3Aalbum%3Aalbum-1',
    ]}
  >
    <Routes>
      <Route
        path="/library/:provider/:view/:artist/:album"
        element={<SongList isSelecting={false} registerMusicToCard={vi.fn()} />}
      />
    </Routes>
  </MemoryRouter>,
);

describe('Jellyfin song list', () => {
  beforeEach(() => {
    request.mockReset();
  });

  afterEach(() => {
    vi.clearAllMocks();
  });

  test('fetches the song list with the album content_uri and the jellyfin provider', async () => {
    request.mockResolvedValue({ result: jellyfinSongs, error: null });
    renderSongList();

    expect(await screen.findByText('Track One')).toBeInTheDocument();
    expect(request).toHaveBeenCalledWith('songList', {
      album: 'Album One',
      albumartist: 'Artist One',
      content_uri: 'service:jellyfin:album:album-1',
      provider: 'jellyfin',
    });
  });

  test('play button requests play_album with content_uri and provider', async () => {
    const user = userEvent.setup();
    const registerMusicToCard = vi.fn();
    render(
      <SongListControls
        albumartist="Artist One"
        album="Album One"
        contentUri="service:jellyfin:album:album-1"
        disabled={false}
        isSelecting={false}
        provider="jellyfin"
        registerMusicToCard={registerMusicToCard}
      />,
    );

    await user.click(screen.getByRole('button', { name: 'Play' }));

    expect(request).toHaveBeenCalledWith('play_album', {
      albumartist: 'Artist One',
      album: 'Album One',
      content_uri: 'service:jellyfin:album:album-1',
      provider: 'jellyfin',
    });
  });

  test('registering a Jellyfin album to a card preserves content_uri and provider', async () => {
    const user = userEvent.setup();
    const registerMusicToCard = vi.fn();
    render(
      <SongListControls
        albumartist="Artist One"
        album="Album One"
        contentUri="service:jellyfin:album:album-1"
        disabled={false}
        isSelecting
        provider="jellyfin"
        registerMusicToCard={registerMusicToCard}
      />,
    );

    await user.click(screen.getByRole('button', { name: 'assign-to-card' }));

    expect(registerMusicToCard).toHaveBeenCalledWith('play_album', {
      albumartist: 'Artist One',
      album: 'Album One',
      content_uri: 'service:jellyfin:album:album-1',
      provider: 'jellyfin',
    });
  });

  test('clicking a Jellyfin track requests play_single with the stable track URI', async () => {
    const user = userEvent.setup();
    render(
      <SongListItem
        isSelecting={false}
        registerMusicToCard={vi.fn()}
        song={jellyfinSongs[0]}
      />,
    );

    await user.click(screen.getByText('Track One'));

    expect(request).toHaveBeenCalledWith('play_single', {
      song_url: 'service:jellyfin:track:track-1',
      provider: 'jellyfin',
    });
  });

  test('registering a Jellyfin track to a card preserves song_url and provider', async () => {
    const user = userEvent.setup();
    const registerMusicToCard = vi.fn();
    render(
      <SongListItem
        isSelecting
        registerMusicToCard={registerMusicToCard}
        song={jellyfinSongs[0]}
      />,
    );

    await user.click(screen.getByText('Track One'));

    expect(registerMusicToCard).toHaveBeenCalledWith('play_single', {
      song_url: 'service:jellyfin:track:track-1',
      provider: 'jellyfin',
    });
  });
});
