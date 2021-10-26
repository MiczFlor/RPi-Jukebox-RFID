import React from 'react';

import {
  Grid,
  Typography,
} from '@mui/material';

const SongListHeadline = ({ song }) => (
  <Grid container sx={{ padding: '16px 8px 0' }}>
    <Grid item>
      {song &&
        <>
          <Typography variant="h6" sx={{ fontWeight: 'bold' }} component="h1">
            {song?.album}
          </Typography>
          <Typography>{song?.albumartist}</Typography>
        </>
      }
    </Grid>
  </Grid>
);

export default SongListHeadline;
