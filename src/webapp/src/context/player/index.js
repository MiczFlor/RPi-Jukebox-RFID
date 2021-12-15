import React, { useEffect, useState } from 'react';

import PlayerContext from './context';
import { initSockets } from '../../sockets';

const PlayerProvider = ({ children }) => {
  const [state, setState] = useState({});

  // Initialize sockets for player context
  useEffect(() => {
    initSockets({
      events: ['playerstatus'],
      setState,
    });
  }, []);

  const context = {
    setState,
    state,
  };

  // Should be called <PlayerFunctions.Provider />
  // and `state` should be moved to PlayerStatus.Provider

  return(
      <PlayerContext.Provider value={context}>
        { children }
      </PlayerContext.Provider>
    )
};

export default PlayerProvider;
