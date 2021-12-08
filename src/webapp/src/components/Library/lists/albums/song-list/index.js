import React, { useEffect, useState } from 'react';
import { useParams } from 'react-router';

import {
  CircularProgress,
  Grid,
  List,
  Typography,
} from '@mui/material';

import request from '../../../../../utils/request';

import SongListHeader from './song-list-header';
import SongListHeadline from './song-list-headline';
import SongListControls from './song-list-controls';
import SongListItem from './song-list-item';

const SongList = () => {
  const { artist, album } = useParams();
  const [songs, setSongs] = useState([]);
  const [error, setError] = useState(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const getSongList = async () => {
      setIsLoading(true);
      const { result, error } = await request(
        'songList',
        {
          album: decodeURIComponent(album),
          albumartist: decodeURIComponent(artist),
        }
      );
      setIsLoading(false);

      if(result) {
        setSongs(result);
      }
      if(error) setError(error);
    }

    getSongList();
  }, [album, artist]);

  return (
    <Grid container id="song-list">
      <SongListHeader />
      <SongListHeadline
        album={decodeURIComponent(album)}
        artist={decodeURIComponent(artist)}
      />
      <SongListControls
        album={decodeURIComponent(album)}
        albumartist={decodeURIComponent(artist)}
        disabled={songs.length === 0}
      />
      <Grid
        container
        spacing={1}
        sx={{
          display: 'flex',
          justifyContent: 'center',
          marginTop: '0'
        }}
      >
        {isLoading
          ? <CircularProgress />
          : <List sx={{ width: '100%', bgcolor: 'background.paper' }}>
              {songs.map(song =>
                <SongListItem key={song.track} song={song} />
              )}
            </List>
        }
        {error &&
          <Typography>Strange, no songs in this album. 🤔</Typography>
        }
      </Grid>
    </Grid>
  );
}

export default React.memo(SongList);
