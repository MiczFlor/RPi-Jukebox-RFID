import { forwardRef, useContext, useEffect, useRef, useState } from 'react';
import {
  Link,
  useLocation,
} from 'react-router-dom';
import { useTranslation } from 'react-i18next';

import {
  Avatar,
  ListItem,
  ListItemAvatar,
  ListItemButton,
  ListItemText,
} from '@mui/material';

import noCover from '../../../../../assets/noCover.jpg';

import AppSettingsContext from '../../../../../context/appsettings/context';
import request from '../../../../../utils/request';

// Cover art results are cached at module scope so they survive a component remount (e.g.
// navigating away from and back to the library view) within the same page load - only a full
// page reload clears it. Keyed by content_uri (stable per-provider item id) when available,
// falling back to provider+albumartist+album for providers that don't supply one.
const coverArtCache = new Map();

// The library can list many dozens of albums. Firing a getAlbumCoverArt RPC call for every
// single one on mount - each opening its own connection, all serialized through the
// single-threaded RPC server - is what made the library view slow to load. Lazy-load via
// IntersectionObserver instead, and cap how many fetches run at once so a long scroll still
// doesn't fire dozens of requests in one burst.
const MAX_CONCURRENT_COVER_FETCHES = 10;
let activeCoverFetches = 0;
const pendingCoverFetchQueue = [];

const runNextQueuedFetch = () => {
  if (activeCoverFetches >= MAX_CONCURRENT_COVER_FETCHES) return;
  const next = pendingCoverFetchQueue.shift();
  if (next) next();
};

const scheduleCoverFetch = (fetchFn) => new Promise((resolve) => {
  const task = async () => {
    activeCoverFetches += 1;
    try {
      resolve(await fetchFn());
    } finally {
      activeCoverFetches -= 1;
      runNextQueuedFetch();
    }
  };
  if (activeCoverFetches < MAX_CONCURRENT_COVER_FETCHES) {
    task();
  } else {
    pendingCoverFetchQueue.push(task);
  }
});

const AlbumListItem = ({
  albumartist,
  album,
  content_uri,
  cover_url,
  isButton = true,
  provider = 'mpd',
  view = 'albums',
}) => {
  const { t } = useTranslation();
  const { search: urlSearch } = useLocation();
  const [coverImage, setCoverImage] = useState(cover_url || noCover);
  const itemRef = useRef(null);

  const {
    settings,
  } = useContext(AppSettingsContext);

  const {
    show_covers,
  } = settings;

  useEffect(() => {
    setCoverImage(cover_url || noCover);
    if (cover_url) return undefined;
    if (!albumartist || !album || !show_covers) return undefined;

    const cacheKey = content_uri || `${provider}:${albumartist}:${album}`;

    const applyResult = (result) => {
      if (result && result !== 'CACHE_PENDING') {
        setCoverImage(result.startsWith('http') ? result : `/cover-cache/${result}`);
      }
    };

    const cached = coverArtCache.get(cacheKey);
    if (cached !== undefined) {
      applyResult(cached);
      return undefined;
    }

    const node = itemRef.current;
    if (!node) return undefined;

    const observer = new IntersectionObserver((entries) => {
      if (!entries.some((entry) => entry.isIntersecting)) return;
      observer.disconnect();

      scheduleCoverFetch(async () => {
        const { result } = await request('getAlbumCoverArt', {
          albumartist,
          album,
          content_uri,
          provider,
        });
        // Don't cache a pending marker - a later remount should retry rather than getting
        // stuck showing the placeholder cover forever.
        if (result && result !== 'CACHE_PENDING') {
          coverArtCache.set(cacheKey, result);
        }
        applyResult(result);
        return result;
      });
    }, { rootMargin: '200px' });

    observer.observe(node);
    return () => observer.disconnect();
  }, [albumartist, album, content_uri, cover_url, provider, show_covers]);

  const AlbumLink = forwardRef((props, ref) => {
    const artist = encodeURIComponent(albumartist || t('library.albums.unknown-artist'));
    const encodedAlbum = encodeURIComponent(album || t('library.albums.unknown-album'));

    const searchParams = new URLSearchParams(urlSearch);
    if (content_uri) searchParams.set('content_uri', content_uri);
    else searchParams.delete('content_uri');
    const search = searchParams.toString();
    const location = [
      `/library/${provider}/${view}/${artist}/${encodedAlbum}`,
      search ? `?${search}` : '',
    ].join('');

    return <Link ref={ref} to={location} {...props} />
  });
  AlbumLink.displayName = 'AlbumLink';

  const content = (
    <>
      {show_covers &&
        <ListItemAvatar>
          <Avatar variant="rounded" alt="Cover" src={coverImage} />
        </ListItemAvatar>
      }
      <ListItemText
        primary={album || t('library.albums.unknown-album')}
        secondary={albumartist || null}
      />
    </>
  );

  return (
    <ListItem ref={itemRef} disablePadding={isButton} key={content_uri || album}>
      {isButton
        ? (
          <ListItemButton component={AlbumLink} nativeButton={false}>
            {content}
          </ListItemButton>
        )
        : content
      }
    </ListItem>
  );
}

export default AlbumListItem;
