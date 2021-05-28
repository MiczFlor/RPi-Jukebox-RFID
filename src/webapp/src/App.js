import React from 'react';
import SocketProvider from './context/sockets';

import Grid from '@material-ui/core/Grid';

import Player from './components/Player';
import Navigation from './components/Navigation';

function App() {
  return (
    <SocketProvider>
      <Grid container direction="row" justify="center" alignItems="center">
        <Grid item xs={12} sm={6}>
          <Player />
          <Navigation />
        </Grid>
      </Grid>
    </SocketProvider>
  );
}

export default App;
