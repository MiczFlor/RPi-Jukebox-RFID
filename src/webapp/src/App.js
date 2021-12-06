import React from 'react';

import Grid from '@mui/material/Grid';

import PlayerProvider from './context/player';
import Router from './router';

function App() {
  return (
    <PlayerProvider>
      <Grid
        alignItems="center"
        container
        direction="row"
        id="routes"
        justifyContent="center"
      >
        <Router />
      </Grid>
    </PlayerProvider>
  );
}

export default App;
