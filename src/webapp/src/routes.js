import React from 'react'
import { Route, HashRouter, Switch } from 'react-router-dom'

import Player from './components/Player'
import Settings from './components/Settings'
import Navigation from './components/Navigation';

const Routes = (props) => (
  <HashRouter>
    <Switch>
      <Route exact path='/'>
        <Player />
      </Route>
      <Route exact path='/settings'>
        <Settings />
      </Route>
    </Switch>
    <Navigation />
  </HashRouter>
);

export default Routes