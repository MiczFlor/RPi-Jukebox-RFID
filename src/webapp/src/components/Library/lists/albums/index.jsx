import { useEffect, useState } from "react";
import { useTranslation } from 'react-i18next';

import {
  CircularProgress,
  Typography,
} from "@mui/material";

import request from '../../../../utils/request';
import { flatByAlbum } from '../../../../utils/utils';

import AlbumList from "./album-list";

const Albums = ({
  contentTypes,
  musicFilter,
  provider,
  view,
}) => {
  const { t } = useTranslation();

  const [albums, setAlbums] = useState([]);
  const [error, setError] = useState(null);
  const [isLoading, setIsLoading] = useState(true);

  const search = ({ albumartist, album }) => {
    if (musicFilter === '') return true;

    const lowerCaseMusicFilter = musicFilter.toLowerCase();

    return (albumartist || '').toLowerCase().includes(lowerCaseMusicFilter) ||
      (album || '').toLowerCase().includes(lowerCaseMusicFilter);
  };

  const contentTypesKey = contentTypes?.join(',') || '';

  useEffect(() => {
    let isCurrent = true;
    const fetchAlbumList = async () => {
      setIsLoading(true);
      setError(null);
      const { result, error: requestError } = await request('libraryItems', {
        provider,
        content_types: contentTypesKey ? contentTypesKey.split(',') : undefined,
      });
      if (!isCurrent) return;
      setIsLoading(false);

      if(result) setAlbums(result.reduce(flatByAlbum, []));
      if(requestError) setError(requestError);
    }

    fetchAlbumList();
    return () => {
      isCurrent = false;
    };
  }, [contentTypesKey, provider]);

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
