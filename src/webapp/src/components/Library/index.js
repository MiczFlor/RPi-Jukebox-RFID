import React from 'react';
import {
  Navigate,
  Route,
  Routes,
  useLocation,
} from 'react-router-dom';

import LibraryLists from './lists';

const Library = () => {
  const { search: urlSearch } = useLocation();
  const lastListView =
    `${localStorage.getItem('libraryLastListView') || 'albums'}${urlSearch}`;

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
    </Routes>
  );
};

export default Library;
