import { createContext } from 'react';

const PlayerContext = createContext({
  playerstatus: {},
  isPlaying: false,
  requestInFlight: false,
});

export default PlayerContext;
