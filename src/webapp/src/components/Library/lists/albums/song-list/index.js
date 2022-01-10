import React, { useEffect, useState } from 'react';
import { useParams } from 'react-router';
import { useTranslation } from 'react-i18next';

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

const SongList = ({
  isSelecting,
  registerMusicToCard,
}) => {
  const { t } = useTranslation();
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
        isSelecting={isSelecting}
        registerMusicToCard={registerMusicToCard}
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
          : <List sx={{ width: '100%' }}>
              {songs.map(song =>
                <SongListItem
                  key={song.track}
                  song={song}
                  isSelecting={isSelecting}
                  registerMusicToCard={registerMusicToCard}
                />
              )}
            </List>
        }
        {error &&
          <Typography>{`${t('library.albums.no-songs-in-album')} 🤔`}</Typography>
        }
      </Grid>
    </Grid>
  );
}

export default React.memo(SongList);
