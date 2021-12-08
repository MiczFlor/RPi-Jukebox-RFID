import React from 'react';

import Grid from '@mui/material/Grid';

import Cover from './cover';
import Controls from './controls';
import Display from './display';
import SeekBar from './seekbar';
import Volume from './volume';

const Player = () => {
  return (
    <Grid
      container
      id="player"
      sx={{
        padding: '10px',
        background: 'brown'
      }}
    >
      <Grid
       item xs={12}
      sx={{
        paddingTop: '20px',
        paddingLeft: '20px',
        paddingRight: '20px',
        minHeight: 'calc(100vh - 64px - 20px)'
      }}
      >
        <Grid item xs={12} sm={5}>
          <Cover />
        </Grid>
        <Grid item xs={12} sm={7}>
          <Display />
          <SeekBar />
          <Controls />
          <Volume />
        </Grid>
      </Grid>
    </Grid>
  );
};

export default Player;
