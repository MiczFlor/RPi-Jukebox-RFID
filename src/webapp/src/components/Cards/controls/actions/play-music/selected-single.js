import React, { useEffect, useState } from 'react';
import { useTranslation } from 'react-i18next';

import { CircularProgress, Grid, List, Typography } from '@mui/material';

import SongListItem from '../../../../Library/lists/albums/song-list/song-list-item'
import NoMusicSelected from './no-music-selected';

import request from '../../../../../utils/request';

const SelectecSingle = ({ values: [song_url] }) => {
  const { t } = useTranslation();
  const [song, setSong] = useState({});
  const [error, setError] = useState(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const getSongList = async () => {
      setIsLoading(true);
      const { result, error } = await request('getSongByUrl', { song_url });
      setIsLoading(false);

      if(result) {
        setSong(result[0]);
      }
      if(error) setError(error);
    }

    getSongList();
  }, [song_url]);

  if (error) {
    return (
      <Typography>
        {t('cards.controls.actions.play-music.loading-song-error')}
      </Typography>
    );
  }

  if (isLoading) {
    return (
      <Grid
        container
        sx={{
            display: 'flex',
            justifyContent: 'center',
            marginTop: '20px',
            marginBottom: '20px',
          }}>
        <CircularProgress size={20} />
      </Grid>
    );
  }

  if (song_url) {
    return (
      <List sx={{ width: '100%' }}>
        <SongListItem song={song} />
      </List>
    );
  }

  return <NoMusicSelected />
};

export default SelectecSingle;
