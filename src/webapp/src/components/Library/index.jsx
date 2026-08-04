import {
  Navigate,
  Route,
  Routes,
  useLocation,
} from 'react-router-dom';

import LibraryLists from './lists';

const Library = () => {
  const { search: urlSearch } = useLocation();
  const storedView = localStorage.getItem('libraryLastListView');
  const migratedView = {
    albums: 'mpd/albums',
    folders: 'mpd/folders/.%2F',
  }[storedView] || storedView || 'overview';
  const lastListView = `${migratedView}${urlSearch}`;

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
