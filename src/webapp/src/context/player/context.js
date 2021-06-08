import { createContext } from 'react';

import { DEFAULT_PLAYER_STATUS } from '../../config';

const PlayerContext = createContext({
  playerstatus: DEFAULT_PLAYER_STATUS.kwargs.status,
  isPlaying: false,
  requestInFlight: false,
  postJukeboxCommand: async () => {},
});

export default PlayerContext;
