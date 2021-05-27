import React, { useContext } from 'react';

import { PlayerStatusContext } from '../../context/playerStatus';

import Box from '@material-ui/core/Box';
import LinearProgress from '@material-ui/core/LinearProgress';

const Display = () => {
  const [ playerStatus ] = useContext(PlayerStatusContext);

  const { params: { status } } = playerStatus;

  return (
    <Box my={4}>
      {
        status?.songid ?
        <p>{status?.title}</p> :
        <p>No song in queue</p>
      }
      <LinearProgress variant="determinate" value="40" />
    </Box>
  );
};

export default Display;
