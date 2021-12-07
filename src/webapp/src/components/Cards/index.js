import React from 'react';
import {
  Route,
  Routes,
} from 'react-router-dom';

import CardsOverview from './overview';
import CardsManage from './manage';

const Cards = () => {
  return (
    <Routes>
      <Route
        index
        element={<CardsOverview />}
      />
      <Route
        path="register"
        element={<CardsManage/>}
      />
      <Route
        path=":cardId/edit"
        element={<CardsManage/>}
      />
    </Routes>
  );
};

export default Cards;
