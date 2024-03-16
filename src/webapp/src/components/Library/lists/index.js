import React, { useState } from "react";
import {
  Navigate,
  Route,
  Routes,
  useLocation,
  useNavigate,
  useSearchParams,
} from 'react-router-dom';

import {
  Grid,
} from '@mui/material';

import Albums from './albums';
import SongList from './albums/song-list';
import Folders from './folders';
import LibraryHeader from "../library-header";
import SelectorHeader from "../selector-header";

import { buildActionData } from '../../Cards/utils';

const LibraryLists = () => {
  const navigate = useNavigate();
  const { search: urlSearch } = useLocation();
  const [searchParams] = useSearchParams();
  const [isSelecting] = useState(searchParams.get('isSelecting'));
  const [cardId] = useState(searchParams.get('cardId'));
  const [musicFilter, setMusicFilter] = useState('');

  const handleMusicFilter = (event) => {
    setMusicFilter(event.target.value);
  };

  const registerMusicToCard = (command, args) => {
    const actionData = buildActionData('play_music', command, args);
    const state = {
      registerCard: {
        actionData,
        cardId,
      },
    };

    navigate('/cards/register', { state });
  };

  return (
    <Grid container id="library">
      {isSelecting && <SelectorHeader />}
      <Grid container sx={{ padding: '10px' }}>
        <LibraryHeader
          handleMusicFilter={handleMusicFilter}
          musicFilter={musicFilter}
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
              element={<Albums musicFilter={musicFilter} />}
              exact
            />
            <Route
              path="albums/:artist/:album"
              element={
                <SongList
                  isSelecting={isSelecting}
                  registerMusicToCard={registerMusicToCard}
                />
              }
              exact
            />
            <Route
              path="folders"
              element={<Navigate to={`.%2F${urlSearch}`} replace />}
            />
            <Route
              path="folders/:dir"
              element={
                <Folders
                  musicFilter={musicFilter}
                  isSelecting={isSelecting}
                  registerMusicToCard={registerMusicToCard}
                />
              }
            />
          </Routes>
        </Grid>
      </Grid>
    </Grid>
  );
};

export default LibraryLists;
