import React, { useEffect, useState } from "react";
import {
  Redirect,
  Route,
  Switch,
  useHistory,
  useRouteMatch,
} from 'react-router-dom';

import { Grid } from '@mui/material';

import Albums from './albums';
import Folders from './folders';
import LibraryHeader from "../library-header";

const LibraryLists = () => {
  const history = useHistory();
  const { path } = useRouteMatch();

  const [view, setView] = useState('albums');
  const [searchQuery, setSearchQuery] = useState('');

  const handleSearch = (event) => {
    setSearchQuery(event.target.value);
  };

  useEffect(() => {
    history.push(`${path}/${view}`);
  }, [view, history, path])

  return (
    <>
      <LibraryHeader
        handleSearch={handleSearch}
        searchQuery={searchQuery}
        view={view}
        setView={setView}
      />
      <Grid
        container
        spacing={1}
        sx={{
          display: 'flex',
          justifyContent: 'center',
        }}
      >
        <Switch>
          <Route exact path={`${path}/albums`}>
            <Albums searchQuery={searchQuery} />
          </Route>
          <Route path={`${path}/folders/:dir`}>
            <Folders searchQuery={searchQuery} />
          </Route>
          <Route path={`${path}/folders`}>
            <Redirect to={`${path}/folders/.%2F`} />
          </Route>
        </Switch>
      </Grid>
    </>
  );
};

export default LibraryLists;
