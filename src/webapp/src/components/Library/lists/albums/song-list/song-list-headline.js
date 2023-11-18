import React from 'react';

import {
  Grid,
  Typography,
} from '@mui/material';

const SongListHeadline = ({ artist, album }) => (
  <Grid container sx={{ padding: '16px 8px 0' }}>
    <Grid item>
      <Typography variant="h6" sx={{ fontWeight: 'bold' }} component="h1">
        {album}
      </Typography>
      <Typography>{artist}</Typography>
    </Grid>
  </Grid>
);

export default SongListHeadline;
