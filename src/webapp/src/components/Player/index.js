import React, { useState, useContext, useCallback, useEffect } from 'react';
import { SocketContext } from '../../context/socket';
import { encodeMessage } from '../../utils/socketMessage';

import Button from '@material-ui/core/Button';
import Box from '@material-ui/core/Box';

import Display from './display'

const Player = () => {
  const socket = useContext(SocketContext);

  const [hasList, setHasList] = useState(false);
  const [isPlaying, setIsPlaying] = useState(false);

  useEffect(() => {
    socket.send(
      encodeMessage({object: 'player', method: 'playerstatus', params: {}})
    );
  }, [socket]);

  const play = useCallback(() => {
    console.log('hasList', hasList);
    let obj;

    if(hasList) {
      obj = {
        "object": "player",
        "method": "play",
        "params": {}
      };
    }

    if(!hasList) {
      obj = {
        "object": "player",
        "method": "playlistaddplay",
        "params": {
          "folder": "kita1"
        }
      };

      setHasList(true);
    }

    setIsPlaying(true);
    socket.send(encodeMessage(obj));
  }, [hasList]);

  const stop = useCallback(() => {
    const obj = {
      "object": "player",
      "method": "stop",
      "params": {}
    };

    setIsPlaying(false);
    socket.send(encodeMessage(obj));
  }, []);

  const pause = useCallback(() => {
    const obj = {
      "object": "player",
      "method": "pause",
      "params": {}
    };

    setIsPlaying(false);
    socket.send(encodeMessage(obj));
  }, []);

  const previous = useCallback(() => {
    const obj = {
      "object": "player",
      "method": "prev",
      "params": {}
    };

    setIsPlaying(true);
    socket.send(encodeMessage(obj));
  }, []);

  const next = useCallback(() => {
    const obj = {
      "object": "player",
      "method": "next",
      "params": {}
    };

    setIsPlaying(true);
    socket.send(encodeMessage(obj));
  }, []);

  return (
    <div id="player">
      <Display />
      <Box my={4}>
        <Button variant="contained" onClick={previous}>Previous</Button>
        {!isPlaying && <Button variant="contained" onClick={play}>Play</Button>}
        {isPlaying && <Button variant="contained" onClick={pause}>Pause</Button>}
        <Button variant="contained" onClick={stop}>Stop</Button>
        <Button variant="contained" onClick={next}>Next</Button>
      </Box>
    </div>
  );
};

export default Player;
