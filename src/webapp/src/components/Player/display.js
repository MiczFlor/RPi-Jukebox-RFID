import React, { useCallback, useContext, useEffect, useState} from 'react';
import { SocketContext } from '../../context/socket';
import { decodeMessage } from '../../utils/socketMessage';

import Box from '@material-ui/core/Box';
import LinearProgress from '@material-ui/core/LinearProgress';

const Display = () => {
  const socket = useContext(SocketContext);

  const [response, setResponse] = useState({});

  // const getPlayerStatus

  const handleDisplayUpdate = useCallback((msg) => {
    const { object, params } = decodeMessage(msg);
    
    if(object === 'player') {
      setResponse(params);
    }
  });

  useEffect(() => {
    socket.on('message', handleDisplayUpdate);
  }, [socket]);

  return (
    <Box my={4}>
      <p>Playing: {response.title}</p>
      <LinearProgress variant="determinate" value="40" />
    </Box>
  );
};

export default Display;
