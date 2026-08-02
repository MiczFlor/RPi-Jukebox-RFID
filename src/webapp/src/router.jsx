import { lazy } from 'react';
import { Route, HashRouter, Routes } from 'react-router-dom'

import Navigation from './components/Navigation';

import Grid from '@mui/material/Grid';

const Cards = lazy(() => import('./components/Cards'));
const Library = lazy(() => import('./components/Library'));
const Player = lazy(() => import('./components/Player'));
const Settings = lazy(() => import('./components/Settings'));

const Router = () => {
  return (
    <HashRouter>
      <Grid
        component="main"
        size={{ xs: 12, md: 6 }}
        sx={{
          marginBottom: '64px',
        }}
      >
        <Routes>
          <Route
            index
            element={<Player/>}
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
          />
        </Routes>
      </Grid>
      <Navigation />
    </HashRouter>
  );
}

export default Router;
