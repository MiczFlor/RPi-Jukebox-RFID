import React from 'react';
import {
  Route,
  Switch,
  useRouteMatch,
} from 'react-router-dom';

import LibraryLists from './lists';
import SongList from './lists/albums/song-list';

const Library = () => {
  const { path } = useRouteMatch();

  return (
    <Switch>
      <Route exact path={`${path}/albums/:artist/:album`}>
        <SongList />
      </Route>
      <Route path={`${path}`}>
        <LibraryLists />
      </Route>
    </Switch>
  );
};

export default Library;
