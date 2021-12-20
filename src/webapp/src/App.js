import React from 'react';

import Grid from '@mui/material/Grid';

import PubSubProvider from './context/pubsub';
import PlayerProvider from './context/player';
import Router from './router';

function App() {
  return (
    <PubSubProvider>
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
    </PubSubProvider>
  );
}

export default App;
