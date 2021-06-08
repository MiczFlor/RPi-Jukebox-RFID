import React from 'react'
import { Route, HashRouter, Switch } from 'react-router-dom'

import Library from './components/Library';
import Navigation from './components/Navigation';
import Player from './components/Player'
import Settings from './components/Settings'

const Routes = (props) => (
  <HashRouter>
    <Switch>
      <Route exact path='/'>
        <Player />
      </Route>
      <Route exact path='/library'>
        <Library />
      </Route>
      <Route exact path='/settings'>
        <Settings />
      </Route>
    </Switch>
    <Navigation />
  </HashRouter>
);

export default Routes