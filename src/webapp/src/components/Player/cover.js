import React from 'react';
import { useTranslation } from 'react-i18next';

import Grid from '@mui/material/Grid';
import Paper from '@mui/material/Paper';
import MusicNoteIcon from '@mui/icons-material/MusicNote';

const Cover = ({ coverImage }) => {
  const { t } = useTranslation();

  return (
    <Grid container direction="row" justifyContent="center" alignItems="center">
      <Paper
        elevation={3}
        sx={{
          width: '70%',
          position: 'relative',
          paddingBottom: '70%',
        }}
      >
        <Grid
          container
          direction="row"
          justifyContent="center"
          alignItems="center"
          sx={{
            position: 'absolute',
            width: '100%',
            height: '100%',
          }}
        >
          {coverImage &&
            <img
              alt={t('player.cover.title')}
              src={`data:image/jpeg;base64,${coverImage}`}
              style={{ width: '100%', height: '100%' }}
            />}
          {!coverImage &&
            <MusicNoteIcon
              style={{ fontSize: 75 }}
              title={t('player.cover.unavailable')}
            />
          }
        </Grid>
      </Paper>
    </Grid>
  );
};

export default Cover;
