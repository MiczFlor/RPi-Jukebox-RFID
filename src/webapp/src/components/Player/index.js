import React, { useState, useContext, useCallback, useEffect, useRef } from 'react';
import { SocketContext } from '../../context/socket';

import Button from '@material-ui/core/Button';
import Box from '@material-ui/core/Box';

import Display from './display'

const Player = () => {
  const socket = useContext(SocketContext);

  const [hasList, setHasList] = useState(false);
  const [isPlaying, setIsPlaying] = useState(false);
  const hasListRef = useRef();
  hasListRef.current = hasList;


  useEffect(() => {
    socket.send(JSON.stringify({object: 'player', method: 'playerstatus', params: {}}));
  }, [socket]);

  const play = useCallback(() => {
    console.log('hasList', hasList);
    let obj;

    if(hasListRef.current) {
      obj = JSON.stringify({
        "object": "player",
        "method": "play",
        "params": {}
      });
    }

    if(!hasListRef.current) {
      obj = JSON.stringify({
        "object": "player",
        "method": "playlistaddplay",
        "params": {
          "folder": "kita1"
        }
      });

      setHasList(true);
    }

    setIsPlaying(true);
    socket.send(obj);
  }, []);

  const stop = useCallback(() => {
    const obj = JSON.stringify({
      "object": "player",
      "method": "stop",
      "params": {}
    });

    setIsPlaying(false);
    socket.send(obj);
  }, []);

  const pause = useCallback(() => {
    const obj = JSON.stringify({
      "object": "player",
      "method": "pause",
      "params": {}
    });

    setIsPlaying(false);
    socket.send(obj);
  }, []);

  const previous = useCallback(() => {
    const obj = JSON.stringify({
      "object": "player",
      "method": "prev",
      "params": {}
    });

    socket.send(obj);
  }, []);

  const next = useCallback(() => {
    const obj = JSON.stringify({
      "object": "player",
      "method": "next",
      "params": {}
    });

    socket.send(obj);
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
