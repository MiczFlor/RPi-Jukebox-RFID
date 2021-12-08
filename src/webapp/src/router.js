import React from 'react'
import { Route, HashRouter, Routes } from 'react-router-dom'

import Cards from './components/Cards';
import Library from './components/Library';
import Navigation from './components/Navigation';
import Player from './components/Player'
import Settings from './components/Settings'

import Grid from '@mui/material/Grid';

const Router = () => {
  return (
    <HashRouter>
      <Grid
        item xs={12}
        md={6}
        sx={{
          marginBottom: '64px',
        }}
      >
        <Routes>
          <Route
            index
            element={<Player/>}
            exact
          />
          <Route
            path="library/*"
            element={<Library/>}
          />
          <Route
            path="cards/*"
            element={<Cards/>}
          />
          <Route
            path="settings/*"
            element={<Settings/>}
            exact
          />
        </Routes>
      </Grid>
      <Navigation />
    </HashRouter>
  );
}

export default Router;
