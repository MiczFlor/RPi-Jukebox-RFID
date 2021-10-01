import React from 'react';

import Grid from '@mui/material/Grid';
import Paper from '@mui/material/Paper';
import MusicNoteIcon from '@mui/icons-material/MusicNote';

const Cover = () => {
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
          <MusicNoteIcon style={{ fontSize: 75 }} />
        </Grid>
      </Paper>
    </Grid>
  );
};

export default Cover;
