import React, { useContext, useEffect, useState } from 'react';
import { useParams } from 'react-router';
import { dropLast, head } from 'ramda';

import {
  CircularProgress,
  Grid,
  List,
  Typography,
} from '@mui/material';

import PlayerContext from '../../../context/player/context';
import { fetchSongList } from '../../../utils/requests';

import SongListHeader from './song-list-header';
import SongListHeadline from './song-list-headline';
import SongListControls from './song-list-controls';
import SongListItem from './song-list-item';

const SongList = () => {
  const { play, playSong } = useContext(PlayerContext);
  // const play = () => {}
  // const playSong = () => {}
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
      const { result, error } = await fetchSongList(
        decodeURIComponent(artist),
        decodeURIComponent(album)
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

  console.log('render2')

  return (
    <div id="song-list">
      <SongListHeader song={firstSong} />
      <SongListHeadline song={firstSong} />
      <SongListControls
        song={firstSong}
        getDirectoryPathFromSong={getDirectoryPathFromSong}
        play={play}
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
                <SongListItem key={song.track} song={song} playSong={playSong} />
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
