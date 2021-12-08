import React from 'react';
import {
  Navigate,
  Route,
  Routes,
} from 'react-router-dom';

import Grid from '@mui/material/Grid';

import LibraryLists from './lists';
import SongList from './lists/albums/song-list';

const Library = () => {
  const lastListView = localStorage.getItem('libraryLastListView') || 'albums';

  return (
    <Grid
      container
      id="library"
      sx={{
        padding: '10px',
      }}
    >
      <Routes>
        <Route
          index
          element={<Navigate to={lastListView} replace />}
          exact
        />
        <Route
          path="*"
          element={<LibraryLists />}
        />
        <Route
          path="albums/:artist/:album"
          element={<SongList />}
          exact
        />
      </Routes>
    </Grid>
  );
};

export default Library;
