import React from 'react';
import {
  Route,
  Routes,
} from 'react-router-dom';

import CardsOverview from './overview';
import CardsRegister from './register';
import CardsEdit from './edit';

const Cards = () => {
  return (
    <Routes>
      <Route
        index
        element={<CardsOverview />}
      />
      <Route
        path="register"
        element={<CardsRegister/>}
      />
      <Route
        path=":cardId/edit"
        element={<CardsEdit/>}
      />
    </Routes>
  );
};

export default Cards;
