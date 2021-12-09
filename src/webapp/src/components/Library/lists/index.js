import React, { useState } from "react";
import {
  Navigate,
  Route,
  Routes,
} from 'react-router-dom';

import { Grid } from '@mui/material';

import Albums from './albums';
import Folders from './folders';
import LibraryHeader from "../library-header";

const LibraryLists = () => {
  const [searchQuery, setSearchQuery] = useState('');

  const handleSearch = (event) => {
    setSearchQuery(event.target.value);
  };

  return (
    <>
      <LibraryHeader
        handleSearch={handleSearch}
        searchQuery={searchQuery}
      />
      <Grid
        container
        spacing={1}
        sx={{
          display: 'flex',
          justifyContent: 'center',
        }}
      >
        <Routes>
          <Route
            path="albums"
            element={<Albums searchQuery={searchQuery} />}
            exact
          />
          <Route
            path="folders"
            element={<Navigate to=".%2F" replace />}
          />
          <Route
            path="folders/:dir"
            element={<Folders searchQuery={searchQuery} />}
          />
        </Routes>
      </Grid>
    </>
  );
};

export default LibraryLists;
