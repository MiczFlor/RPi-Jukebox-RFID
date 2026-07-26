import React, { forwardRef, useContext, useEffect, useRef, useState } from 'react';
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
// page reload clears it. Keyed by "albumartist::album".
const coverArtCache = new Map();

// The library can list many dozens of albums. Firing a getAlbumCoverArt RPC call for every
// single one on mount - each opening its own ZeroMQ/WebSocket connection, all serialized through
// the single-threaded RPC server - is what made the library view slow to load. Lazy-load via
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

const AlbumListItem = ({ albumartist, album, isButton = true }) => {
  const { t } = useTranslation();
  const { search: urlSearch } = useLocation();
  const [coverImage, setCoverImage] = useState(noCover);
  const itemRef = useRef(null);

  const {
    settings,
  } = useContext(AppSettingsContext);

  const {
    show_covers,
  } = settings;

  useEffect(() => {
    if (!albumartist || !album || !show_covers) return undefined;

    const cacheKey = `${albumartist}::${album}`;

    const applyResult = (result) => {
      if (result && result !== 'CACHE_PENDING') {
        setCoverImage(`/cover-cache/${result}`);
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
        const { result } = await request('getAlbumCoverArt', { albumartist, album });
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
  }, [albumartist, album, show_covers]);

  const AlbumLink = forwardRef((props, ref) => {
    const { data } = props;

    const artist = encodeURIComponent(data?.albumartist || t('library.albums.unknown-artist'));
    const album = encodeURIComponent(data?.album || t('library.albums.unknown-album'));

    // TODO: Introduce fallback incase artist or album are undefined
    const location = `${artist}/${album}${urlSearch}`;

    return <Link ref={ref} to={location} {...props} />
  });

  return (
    <ListItem
      ref={itemRef}
      button={isButton}
      component={isButton ? AlbumLink : null}
      data={{ albumartist, album }}
      disablePadding
      key={album}
    >
      <ListItemButton>
        {show_covers &&
          <ListItemAvatar>
            <Avatar variant="rounded" alt="Cover" src={coverImage} />
          </ListItemAvatar>
        }
        <ListItemText
          primary={album || t('library.albums.unknown-album')}
          secondary={albumartist || null}
        />
      </ListItemButton>
    </ListItem>
  );
}

export default AlbumListItem;
