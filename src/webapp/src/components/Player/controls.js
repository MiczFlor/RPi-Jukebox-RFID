import React, { useContext } from 'react';

import { PlayerStatusContext } from '../../context/playerStatus';

import Button from '@material-ui/core/Button';
import Box from '@material-ui/core/Box';

const Controls = () => {
  const [ playerStatus, updatePlayerStatus ] = useContext(PlayerStatusContext);
  
  const { params: { status } } = playerStatus;
  
  const isPlaying = status.state === 'play' ? true : false;
  const hasPlaylist = parseInt(status.playlistlength) > 0;

  const play = () => {
    const newPlayerStatus = hasPlaylist
      ? {
        "object": "player",
        "method": "play",
        "params": {}
      }
      : {
        "object": "player",
        "method": "playlistaddplay",
        "params": {
          "folder": "kita1"
        }
      };

    updatePlayerStatus(newPlayerStatus);
  };

  const pause = () => {
    const newPlayerStatus = {
      "object": "player",
      "method": "pause",
      "params": {}
    };

    updatePlayerStatus(newPlayerStatus);
  };

  const previous = () => {
    const newPlayerStatus = {
      "object": "player",
      "method": "prev",
      "params": {}
    };
    
    updatePlayerStatus(newPlayerStatus);
  };

  const next = () => {
    const newPlayerStatus = {
      "object": "player",
      "method": "next",
      "params": {}
    };

    updatePlayerStatus(newPlayerStatus);
  };

  return (
    <Box my={4}>
      <Button variant="contained" onClick={previous}>Previous</Button>
      {!isPlaying && <Button variant="contained" onClick={play}>Play</Button>}
      {isPlaying && <Button variant="contained" onClick={pause}>Pause</Button>}
      <Button variant="contained" onClick={next}>Next</Button>
    </Box>
  );
};

export default Controls;
