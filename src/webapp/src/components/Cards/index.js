import React from 'react';
import {
  Route,
  Routes,
} from 'react-router-dom';

import Grid from '@mui/material/Grid';

import CardsOverview from './overview';
import CardsEdit from './edit';
import CardsRegister from './register';

const Cards = () => {
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
          element={<CardsOverview />}
        />
        <Route
          path=":cardId/edit"
          element={<CardsEdit/>}
        />
        <Route
          path="register"
          element={<CardsRegister/>}
        />
      </Routes>
    </Grid>
  );
};

export default Cards;
