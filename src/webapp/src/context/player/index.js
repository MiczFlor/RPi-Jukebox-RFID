import React, { useState, useEffect } from 'react';

import { DEFAULT_PLAYER_STATUS } from '../../config';
import PlayerContext from './context';
import { initSockets, socketRequest } from '../../sockets';
import { preparePayload } from '../../sockets/utils';

const PlayerProvider = ({ children }) => {
  const postJukeboxCommand = async (plugin, method, kwargs = {}) => {
    setState({ ...state, requestInFlight: true });

    const payload = preparePayload(plugin, method, kwargs);
    const { status } = await socketRequest(payload);

    if(!status) {
      // TODO: Implement error handling as this shouldn't happen
      setState({ ...state, playerstatus: DEFAULT_PLAYER_STATUS });
    }

    setState({ ...state, playerstatus: status });
    setState({ ...state, requestInFlight: false });
  }

  const [state, setState] = useState({
    // Provide a status even when there is not data or
    // or insufficient data coming from the server
    status: DEFAULT_PLAYER_STATUS.kwargs.status,

    // To react immediately to user input, we control the
    // playing status separately, otherwise there is a short
    // lack in response based on the publish events coming
    // from the server
    isPlaying: false,

    // requestInFlight is required to prevent sending requests
    // to the server while another request is still being
    // processed this can happen when users click an action in
    // a very fast manner
    requestInFlight: false,

    // Method to safely execute an existing command on the
    // server
    postJukeboxCommand,
  });


  // All global player actions available across the entire app

  const play = (directory) => {
    if (state.requestInFlight) return;

    const method = directory ? 'playlistaddplay' : 'play';
    const kwargs = method === 'playlistaddplay' ? { folder: directory } : {};

    setState({ ...state, isPlaying: true });
    postJukeboxCommand('player', method, kwargs);
  };

  const pause = () => {
    if (state.requestInFlight) return;

    setState({ ...state, isPlaying: false });
    postJukeboxCommand('player', 'pause');
  };

  const previous = () => {
    if (state.requestInFlight) return;

    setState({ ...state, isPlaying: true });
    postJukeboxCommand('player', 'prev');
  };

  const next = () => {
    if (state.requestInFlight) return;

    setState({ ...state, isPlaying: true });
    postJukeboxCommand('player', 'next');
  };

  const seek = (newTime) => {
    if (state.requestInFlight) return;

    postJukeboxCommand('player', 'seek', { newTime: newTime.toFixed(3) });
  }


  // Initialize sockets for player context
  useEffect(() => {
    initSockets({ setState });
  }, []);

  const context = {
    next,
    pause,
    play,
    previous,
    seek,
    state,
    setState
  };

  return(
      <PlayerContext.Provider value={context}>
        { children }
      </PlayerContext.Provider>
    )
};
export default PlayerProvider;
