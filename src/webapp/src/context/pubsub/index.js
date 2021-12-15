import React, { useEffect, useState } from 'react';
import { without } from 'ramda';

import PubSubContext from './context';
import { initSockets } from '../../sockets';
import { SUBSCRIPTIONS } from '../../config';

const PubSubProvider = ({ children }) => {
  const [state, setState] = useState({});

  // Initialize sockets for player context
  useEffect(() => {
    initSockets({
      events: without(['playerstatus'], SUBSCRIPTIONS),
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
      <PubSubContext.Provider value={context}>
        { children }
      </PubSubContext.Provider>
    )
};

export default PubSubProvider;
