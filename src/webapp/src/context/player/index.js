import React, { useEffect, useState } from 'react';

import PlayerContext from './context';
import { initSockets, socketRequest } from '../../sockets';

const PlayerProvider = ({ children }) => {
  const postJukeboxCommand = async (_package, plugin, method, kwargs) => {
    setState({ ...state, requestInFlight: true });

    try {
      const { status } = await socketRequest(_package, plugin, method, kwargs) || {};

      if(status) {
        setState({ ...state, playerstatus: status });
      }

      setState({ ...state, requestInFlight: false });

      return Promise.resolve();
    }
    catch(error) {
      setState({ ...state, requestInFlight: false });
      return Promise.reject(error);
    }
  }

  const [state, setState] = useState({
    // requestInFlight is required to prevent sending requests
    // to the server while another request is still being
    // processed. This can happen when users click an action in
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
    postJukeboxCommand('player', 'ctrl', method, kwargs);
  };

  const pause = () => {
    if (state.requestInFlight) return;

    setState({ ...state, isPlaying: false });
    postJukeboxCommand('player', 'ctrl', 'pause');
  };

  const previous = () => {
    if (state.requestInFlight) return;

    setState({ ...state, isPlaying: true });
    postJukeboxCommand('player', 'ctrl', 'prev');
  };

  const next = () => {
    if (state.requestInFlight) return;

    setState({ ...state, isPlaying: true });
    postJukeboxCommand('player', 'ctrl', 'next');
  };

  const seek = (new_time) => {
    if (state.requestInFlight) return;

    postJukeboxCommand('player', 'ctrl', 'seek', { new_time: new_time.toFixed(3) });
  }

  const setVolume = (volume) => {
    if (state.requestInFlight) return;

    postJukeboxCommand('volume', 'ctrl', 'set_volume', { volume });
  }

  const setMaxVolume = (maxVolume) => {
    if (state.requestInFlight) return;

    postJukeboxCommand('volume', 'ctrl', 'set_max_volume', { maxVolume });
  }

  const toggleMuteVolume = (mute_on) => {
    if (state.requestInFlight) return;

    postJukeboxCommand('volume', 'ctrl', 'mute', { mute_on });
  }

  const repeat = (repeat, single) => {
    if (state.requestInFlight) return;

    let mode = null;
    if (!repeat && !single) mode = 'repeat';
    if (repeat && !single) mode = 'single';

    postJukeboxCommand('player', 'ctrl', 'repeatmode', { mode });
  }

  const shuffle = (random) => {
    if (state.requestInFlight) return;

    postJukeboxCommand('player', 'ctrl', 'shuffle', { random });
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
    setState,
    setVolume,
    setMaxVolume,
    state,
    toggleMuteVolume,
    repeat,
    shuffle,
  };

  return(
      <PlayerContext.Provider value={context}>
        { children }
      </PlayerContext.Provider>
    )
};
export default PlayerProvider;
