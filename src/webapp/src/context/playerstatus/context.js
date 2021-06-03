import { createContext } from 'react';

import { DEFAULT_PLAYER_STATUS } from '../../config';

const PlayerstatusContext = createContext({
  playerstatus: DEFAULT_PLAYER_STATUS.kwargs.status,
  postJukeboxCommand: async () => {},
});

export default PlayerstatusContext;
