import React, { useState, useEffect } from 'react';

import { DEFAULT_PLAYER_STATUS } from '../../config';
import PlayerstatusContext from './context';
import { initSockets, socketRequest } from '../../sockets';
import { preparePayload } from '../../sockets/utils';

const PlayerstatusProvider = ({ children }) => {
  const postJukeboxCommand = async (plugin, method, kwargs = {}) => {
    const payload = preparePayload(plugin, method, kwargs);
    const { status } = await socketRequest(payload);

    if(!status) {
      setState({ ...state, playerstatus: DEFAULT_PLAYER_STATUS });
    }

    setState({ ...state, playerstatus: status });
  }

  const [state, setState] = useState({
    status: DEFAULT_PLAYER_STATUS.kwargs.status,
    postJukeboxCommand,
  });

  useEffect(() => {
    initSockets({ setState }); // TODO: PubSub
    postJukeboxCommand('player', 'playerstatus');
  }, []);

  return(
      <PlayerstatusContext.Provider value={state}>
        { children }
      </PlayerstatusContext.Provider>
    )
};
export default PlayerstatusProvider;
