import React from 'react';
import { Link } from 'react-router-dom';

import {
  Grid,
  IconButton,
} from '@mui/material';

import ArrowBackIcon from '@mui/icons-material/ArrowBack';
// import Cover from '../../../Player/cover';

const SongListHeader = () => (
  <Grid container>
    <Grid item xs={2}>
      <IconButton
        aria-label="back"
        component={Link}
        to="/library/lists/albums"
        size="large"
      >
        <ArrowBackIcon />
      </IconButton>
    </Grid>
    <Grid item xs={8} sx={{ marginTop: '18px' }}>
      {/* TODO: Simultaneous requests to RPC seem to be a problem */}
      {/* At least in this situation. Solution might be to queue requests */}
      {/* <Cover song={song} /> */}
    </Grid>
    <Grid item xs={2}></Grid>
  </Grid>
);

export default SongListHeader;
