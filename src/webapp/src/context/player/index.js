import React, { useEffect, useState } from 'react';

import PlayerContext from './context';
import { initSockets } from '../../sockets';

const PlayerProvider = ({ children }) => {
  const [state, setState] = useState({
    // requestInFlight is required to prevent sending requests
    // to the server while another request is still being
    // processed. This can happen when users click an action in
    // a very fast manner
    requestInFlight: false,
  });

  // Initialize sockets for player context
  useEffect(() => {
    initSockets({ setState });
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
