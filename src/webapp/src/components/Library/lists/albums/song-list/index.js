import React, { useEffect, useState } from 'react';
import { useParams } from 'react-router';
import { dropLast, head } from 'ramda';

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

  // We use the first song of the list to retrieve the Album Art
  // TODO: This could be done smarter ;-)
  const [firstSong, setFirstSong] = useState(undefined);

  const getDirectoryPathFromSong = (song) => {
    const { file } = song;
    // Removes the file part of the URI to receive directory only
    return dropLast(1, file.split('/')).join('/')
  }

  useEffect(() => {
    const getSongList = async () => {
      setIsLoading(true);
      const { result, error } = await request(
        'songList',
        {
          artist: decodeURIComponent(artist),
          album: decodeURIComponent(album)
        }
      );
      setIsLoading(false);

      if(result) {
        setSongs(result);
        setFirstSong(head(result));
      }
      if(error) setError(error);
    }

    getSongList();
  }, [album, artist]);

  return (
    <div id="song-list">
      <SongListHeader song={firstSong} />
      <SongListHeadline song={firstSong} />
      <SongListControls
        song={firstSong}
        getDirectoryPathFromSong={getDirectoryPathFromSong}
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
    </div>
  );
}

export default React.memo(SongList);
