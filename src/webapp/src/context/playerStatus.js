import {
  createContext,
  useContext,
  useCallback,
  useEffect,
  useMemo,
  useState,
} from 'react';

import { SocketContext } from './socket';
import {
  decodeMessage,
  encodeMessage,
} from '../utils/socketMessage';

const PlayerStatusContext = createContext({});

const initalStatus = {
  params: {
    song: {},
    status: {
      consume: "0",
      mixrampdb: "0.000000",
      playlist: "1",
      playlistlength: "0",
      random: "0",
      repeat: "0",
      single: "0",
      state: "stop",
      volume: 60,
    }
  }
};

const PlayerStatusProvider = ({ children }) => {
  const socket = useContext(SocketContext);

  const [playerStatus, setPlayerStatus] = useState(initalStatus);

  useEffect(() => {
    socket.on('message', (msg) => setPlayerStatus(decodeMessage(msg)));

    socket.send(
      encodeMessage({object: 'player', method: 'playerstatus', params: {}})
    );
  }, [socket]);

  const updatePlayerStatus = useCallback((msg) => {
    socket.send(encodeMessage(msg));
  }, [socket]);

  const context = useMemo(() => ([
    playerStatus,
    updatePlayerStatus
  ]), [playerStatus]);

  return (
    <PlayerStatusContext.Provider value={context}>
      {children}
    </PlayerStatusContext.Provider>
  )
}

export {
  PlayerStatusContext,
  PlayerStatusProvider,
}
