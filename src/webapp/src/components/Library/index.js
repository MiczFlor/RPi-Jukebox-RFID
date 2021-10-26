import React from 'react';
import { Route, useRouteMatch, Switch } from 'react-router-dom';

import SongList from './song-list';
import LibraryLists from './lists';

const Library = () => {
  const { path } = useRouteMatch();

  return (
    <Switch>
      <Route path={`${path}/lists`}>
        <LibraryLists />
      </Route>
      <Route exact path={`${path}/artists/:artist/albums/:album`}>
        <SongList />
      </Route>
    </Switch>
  );
};

export default Library;
