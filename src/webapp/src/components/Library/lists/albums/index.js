import React, { useEffect, useState } from "react";

import {
  CircularProgress,
  Typography,
} from "@mui/material";

import request from '../../../../utils/request';
import { flatByAlbum } from '../../../../utils/utils';

import AlbumList from "./album-list";

const Albums = ({ searchQuery }) => {
  const [albums, setAlbums] = useState([]);
  const [error, setError] = useState(null);
  const [isLoading, setIsLoading] = useState(true);

  const search = ({ albumartist, album }) => {
    if (searchQuery === '') return true;

    const lowerCaseSearchQuery = searchQuery.toLowerCase();

    return albumartist.toLowerCase().includes(lowerCaseSearchQuery) ||
      album.toLowerCase().includes(lowerCaseSearchQuery);
  };

  useEffect(() => {
    const fetchAlbumList = async () => {
      setIsLoading(true);
      const { result, error } = await request('albumList');
      setIsLoading(false);

      if(result) setAlbums(result.reduce(flatByAlbum, []));
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
            searchQuery={searchQuery}
      />}
      {error &&
        <Typography>An error occurred while loading the library.</Typography>
      }
    </>
  );
};

export default Albums;
