import React, { useEffect, useState } from 'react';

import {
  CircularProgress,
  Grid,
  TextField,
  Typography,
} from '@mui/material';

import AlbumList from './album-list';
import { fetchAlbumList } from '../../utils/requests';

const Library = () => {
  const [albums, setAlbums] = useState([]);
  const [error, setError] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');

  const handleSearch = (event) => {
    setSearchQuery(event.target.value);
  };

  const directoryNameBySearchQuery = ({ albumartist, album }) => {
    if (searchQuery === '') return true;

    const lowerCaseSearchQuery = searchQuery.toLowerCase();

    return albumartist.toLowerCase().includes(lowerCaseSearchQuery) ||
      album.toLowerCase().includes(lowerCaseSearchQuery);
  };

  const flatByAlbum = (albumList, { albumartist, album }) => {
    const list = Array.isArray(album)
      ? album.map(name => ({ albumartist, album: name }))
      : [{ albumartist, album }];

    return [...albumList, ...list];
  };

  useEffect(() => {
    const getAlbumList = async () => {
      setIsLoading(true);
      const { result, error } = await fetchAlbumList();
      setIsLoading(false);

      if(result) setAlbums(result.reduce(flatByAlbum, []));
      if(error) setError(error);
    }

    getAlbumList();
  }, []);

  return (
    <div id="library">
      <form noValidate autoComplete="off">
        <Grid container>
          <Grid item xs={12}>
            <TextField
              id="outlined-basic"
              label="Search"
              onChange={handleSearch}
              value={searchQuery}
              variant="outlined"
              sx={{
                width: '100%',
                marginBottom: '10px',
              }}
            />
          </Grid>
        </Grid>
      </form>
      <Grid
        container
        spacing={1}
        sx={{
          display: 'flex',
          justifyContent: 'center',
        }}
      >
        {isLoading
          ? <CircularProgress />
          : <AlbumList
              albums={albums.filter(directoryNameBySearchQuery)}
              searchQuery={searchQuery}
            />
        }
        {error &&
          <Typography>An error occurred while loading the library.</Typography>
        }
      </Grid>
    </div>
  );
};

export default Library;
