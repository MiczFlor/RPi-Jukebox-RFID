import React, { useState, useEffect } from 'react';

import { DEFAULT_PLAYER_STATUS } from '../../config';
import SocketContext from './context';
import { initSockets } from '../../sockets';

const SocketProvider = ({ children }) => {
  const [value, setValue] = useState({
    playerStatus: DEFAULT_PLAYER_STATUS,
  });

  useEffect(() => initSockets({ setValue }), [initSockets]);

  return(
      <SocketContext.Provider value={value}>
        { children }
      </SocketContext.Provider>
    )
};
export default SocketProvider;
