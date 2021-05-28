import React, { useContext, useState } from 'react';

import SocketContext from '../../context/sockets/context';
import { execCommand } from '../../sockets/emit';

import Box from '@material-ui/core/Box';
import Grid from '@material-ui/core/Grid';
import IconButton from '@material-ui/core/IconButton';
import PlayCircleFilledRoundedIcon from '@material-ui/icons/PlayCircleFilledRounded';
import PauseCircleFilledRoundedIcon from '@material-ui/icons/PauseCircleFilledRounded';
import SkipPreviousRoundedIcon from '@material-ui/icons/SkipPreviousRounded';
import SkipNextRoundedIcon from '@material-ui/icons/SkipNextRounded';

const Controls = () => {
  const { playerStatus: { status } } = useContext(SocketContext);

  // const [isPlaying, setIsPlaying] = useState(status?.state === 'play' ? true : false);
  // const [hasPlaylist, setHasPlaylist] = useState(parseInt(status?.playlistlength) > 0);

  // console.log(isPlaying, hasPlaylist);

  const isPlaying = status?.state === 'play' ? true : false;
  const hasPlaylist = parseInt(status?.playlistlength) > 0;

  const play = () => {
    const folder = 'kita1';

    const method = hasPlaylist ? 'play' : 'playlistaddplay';
    const params = method === 'play' ? {} : { folder };

    execCommand('player', method, params);
  };

  const pause = () => {
    execCommand('player', 'pause');
  };

  const previous = () => {
    execCommand('player', 'prev');
  };

  const next = () => {
    execCommand('player', 'next');
  };

  return (
    <Grid container direction="row" justify="center" alignItems="center">
      <IconButton aria-label="Previous" onClick={previous}>
        <SkipPreviousRoundedIcon style={{ fontSize: 35 }} />
      </IconButton>
      {
        !isPlaying &&
        <IconButton aria-label="Play" onClick={play}>
          <PlayCircleFilledRoundedIcon style={{ fontSize: 75 }} />
        </IconButton>
      }
      {
        isPlaying &&
        <IconButton aria-label="Pause" onClick={pause}>
          <PauseCircleFilledRoundedIcon style={{ fontSize: 75 }} />
        </IconButton>
      }
      <IconButton aria-label="Next" onClick={next}>
        <SkipNextRoundedIcon style={{ fontSize: 35 }} />
      </IconButton>
    </Grid>
  );
};

export default Controls;
