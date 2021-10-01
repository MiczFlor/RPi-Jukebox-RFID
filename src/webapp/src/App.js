import React from 'react';

import Grid from '@mui/material/Grid';

import PlayerProvider from './context/player';
import Routes from './routes';

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
        <Routes />
      </Grid>
    </PlayerProvider>
  );
}

export default App;
