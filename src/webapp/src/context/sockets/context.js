import { createContext } from 'react';

import { DEFAULT_PLAYER_STATUS } from '../../config';

const SocketContext = createContext({
  playerStatus: DEFAULT_PLAYER_STATUS.kwargs.status,
});

export default SocketContext;
