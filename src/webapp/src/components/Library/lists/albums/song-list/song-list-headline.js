import React from 'react';

import {
  Grid,
  Typography,
} from '@mui/material';

const SongListHeadline = ({ artist, album }) => (
  <Grid container sx={{ paddingTop: '16px' }}>
    <Grid item>
      <Typography variant="h6" sx={{ fontWeight: 'bold' }} component="h1">
        {album}
      </Typography>
      <Typography>{artist}</Typography>
    </Grid>
  </Grid>
);

export default SongListHeadline;
