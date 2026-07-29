import React, { useEffect, useState } from "react";
import { useTranslation } from 'react-i18next';

import {
  CircularProgress,
  Typography,
} from "@mui/material";

import request from '../../../../utils/request';
import { flatByAlbum } from '../../../../utils/utils';

import AlbumList from "./album-list";

// The album list rarely changes within a session (only on library updates), but the Albums
// component is unmounted/remounted every time the user navigates away from and back to the
// library (react-router unmounts non-matching routes). Without a cache, every single visit to
// the library re-fetches the entire album list from the server via RPC. Cache it at module scope
// so it survives remounts within the same page load - only a full page reload clears it.
let albumListCache = null;

const Albums = ({ musicFilter }) => {
  const { t } = useTranslation();

  const [albums, setAlbums] = useState(albumListCache || []);
  const [error, setError] = useState(null);
  const [isLoading, setIsLoading] = useState(albumListCache === null);

  const search = ({ albumartist, album }) => {
    if (musicFilter === '') return true;

    const lowerCaseMusicFilter = musicFilter.toLowerCase();

    return albumartist.toLowerCase().includes(lowerCaseMusicFilter) ||
      album.toLowerCase().includes(lowerCaseMusicFilter);
  };

  useEffect(() => {
    if (albumListCache !== null) return;

    const fetchAlbumList = async () => {
      setIsLoading(true);
      const { result, error } = await request('albumList');
      setIsLoading(false);

      if(result) {
        const flattened = result.reduce(flatByAlbum, []);
        albumListCache = flattened;
        setAlbums(flattened);
      }
      if(error) setError(error);
    }

    fetchAlbumList();
  }, []);

  return (
    <>
      {isLoading
        ? <CircularProgress />
        : <AlbumList
            albums={albums.filter(search)}
            musicFilter={musicFilter}
      />}
      {error &&
        <Typography>{t('library.loading-error')}</Typography>
      }
    </>
  );
};

export default Albums;
