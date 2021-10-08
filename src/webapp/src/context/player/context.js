import { createContext } from 'react';

const PlayerContext = createContext({
  playerstatus: {},
  isPlaying: false,
  requestInFlight: false,
  postJukeboxCommand: async () => {},
});

export default PlayerContext;
