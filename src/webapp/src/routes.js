import React from 'react'
import { Route, HashRouter, Switch } from 'react-router-dom'

import Cards from './components/Cards';
import CardsRegister from './components/Cards/register';
import CardsEdit from './components/Cards/edit';
import Library from './components/Library';
import Navigation from './components/Navigation';
import Player from './components/Player'
import Settings from './components/Settings'

import Grid from '@mui/material/Grid';

const Routes = () => {
  return (
    <HashRouter>
      <Grid
        item xs={12}
        md={6}
        sx={{
          margin: '10px',
          marginBottom: '64px',
        }}
      >
        <Switch>
          <Route exact path='/'>
            <Player />
          </Route>
          <Route path='/library'>
            <Library />
          </Route>
          <Route path='/cards/register'>
            <CardsRegister />
          </Route>
          <Route path='/cards/:cardId/edit'>
            <CardsEdit />
          </Route>
          <Route path='/cards'>
            <Cards />
          </Route>
          <Route exact path='/settings'>
            <Settings />
          </Route>
        </Switch>
      </Grid>
      <Navigation />
    </HashRouter>
  );
}

export default Routes;
