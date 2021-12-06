import React from 'react';
import {
  Navigate,
  Route,
  Routes,
} from 'react-router-dom';

import LibraryLists from './lists';
import SongList from './lists/albums/song-list';

const Library = () => {
  const lastListView = localStorage.getItem('libraryLastListView') || 'albums';

  return (
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
  );
};

export default Library;
