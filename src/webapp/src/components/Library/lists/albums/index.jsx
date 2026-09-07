import { useEffect, useState } from "react";
import { useTranslation } from 'react-i18next';

import {
  CircularProgress,
  Typography,
} from "@mui/material";

import request from '../../../../utils/request';
import { flatByAlbum } from '../../../../utils/utils';
import { albumListCache } from '../../../../utils/library-cache';

import AlbumList from "./album-list";

// The album list rarely changes within a session (only on library updates), but the Albums
// component is unmounted/remounted every time the user navigates away from and back to the
// library (react-router unmounts non-matching routes). Without a cache, every single visit to
// the library re-fetches the entire list from the server via RPC. Cached at module scope (see
// utils/library-cache.js), keyed by provider+content-types (the actual query params), so it
// survives remounts within the same page load.
const Albums = ({
  contentTypes,
  musicFilter,
  provider,
  view,
}) => {
  const { t } = useTranslation();

  const contentTypesKey = contentTypes?.join(',') || '';
  const cacheKey = `${provider}:${contentTypesKey}`;
  const cached = albumListCache.get(cacheKey);

  const [albums, setAlbums] = useState(cached || []);
  const [error, setError] = useState(null);
  const [isLoading, setIsLoading] = useState(cached === undefined);

  const search = ({ albumartist, album }) => {
    if (musicFilter === '') return true;

    const lowerCaseMusicFilter = musicFilter.toLowerCase();

    return (albumartist || '').toLowerCase().includes(lowerCaseMusicFilter) ||
      (album || '').toLowerCase().includes(lowerCaseMusicFilter);
  };

  useEffect(() => {
    let isCurrent = true;

    const cachedForKey = albumListCache.get(cacheKey);
    if (cachedForKey !== undefined) {
      setAlbums(cachedForKey);
      setError(null);
      setIsLoading(false);
      return undefined;
    }

    const fetchAlbumList = async () => {
      setIsLoading(true);
      setError(null);
      const { result, error: requestError } = await request('libraryItems', {
        provider,
        content_types: contentTypesKey ? contentTypesKey.split(',') : undefined,
      });
      if (!isCurrent) return;
      setIsLoading(false);

      if(result) {
        const flattened = result.reduce(flatByAlbum, []);
        albumListCache.set(cacheKey, flattened);
        setAlbums(flattened);
      }
      if(requestError) setError(requestError);
    }

    fetchAlbumList();
    return () => {
      isCurrent = false;
    };
  }, [cacheKey, contentTypesKey, provider]);

  return (
    <>
      {isLoading
        ? <CircularProgress />
        : <AlbumList
            albums={albums.filter(search)}
            musicFilter={musicFilter}
            view={view}
      />}
      {error &&
        <Typography>{t('library.loading-error')}</Typography>
      }
    </>
  );
};

export default Albums;
