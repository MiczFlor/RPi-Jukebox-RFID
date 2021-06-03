import React from 'react';
import PlayerstatusProvider from './context/playerstatus';

import Grid from '@material-ui/core/Grid';

import Player from './components/Player';
import Navigation from './components/Navigation';

function App() {
  return (
    <PlayerstatusProvider>
      <Grid container direction="row" justify="center" alignItems="center">
        <Grid item xs={12} sm={6}>
          <Player />
          <Navigation />
        </Grid>
      </Grid>
    </PlayerstatusProvider>
  );
}

export default App;
