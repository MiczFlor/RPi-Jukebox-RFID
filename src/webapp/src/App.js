import React from 'react';
import PlayerProvider from './context/player';

import Grid from '@material-ui/core/Grid';

import Routes from './routes';

function App() {
  return (
    <PlayerProvider>
      <Grid container direction="row" justify="center" alignItems="center">
        <Grid item xs={12} sm={6}>
          <Routes />
        </Grid>
      </Grid>
    </PlayerProvider>
  );
}

export default App;
