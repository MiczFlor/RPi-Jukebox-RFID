import React from 'react';
import PlayerProvider from './context/player';

import Grid from '@material-ui/core/Grid';

import Routes from './routes';

function App() {
  return (
    <PlayerProvider>
      <Grid
        alignItems="center"
        container
        direction="row"
        id="routes"
        justify="center"
      >
        <Routes />
      </Grid>
    </PlayerProvider>
  );
}

export default App;
