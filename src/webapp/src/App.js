import React from 'react';
import PlayerstatusProvider from './context/playerstatus';

import Grid from '@material-ui/core/Grid';

import Routes from './routes';

function App() {
  return (
    <PlayerstatusProvider>
      <Grid container direction="row" justify="center" alignItems="center">
        <Grid item xs={12} sm={6}>
          <Routes />
        </Grid>
      </Grid>
    </PlayerstatusProvider>
  );
}

export default App;
