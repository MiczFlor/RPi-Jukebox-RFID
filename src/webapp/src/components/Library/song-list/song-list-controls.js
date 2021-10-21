import React from 'react';

import {
  Grid,
  IconButton,
} from '@mui/material';

import PlayCircleFilledRoundedIcon from '@mui/icons-material/PlayCircleFilledRounded';

const SongListControls = ({ song, getDirectoryPathFromSong, play }) => (
  <Grid container sx={{ padding: '0 8px' }}>
    <Grid item xs={9}></Grid>
    <Grid item xs={3}
      sx={{
        display: 'flex',
        justifyContent: 'right',
      }}
    >
      <IconButton
        aria-label="Play"
        onClick={e => play(getDirectoryPathFromSong(song))}
        disabled={!song}
        size="large"
      >
        <PlayCircleFilledRoundedIcon color="primary" style={{ fontSize: 64 }} />
      </IconButton>
    </Grid>
  </Grid>
);

export default SongListControls;
