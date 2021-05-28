import React, { useContext, useEffect, useState } from 'react';

import SocketContext from '../../context/sockets/context';
import { execCommand } from '../../sockets/emit';

import Grid from '@material-ui/core/Grid';
import IconButton from '@material-ui/core/IconButton';
import PlayCircleFilledRoundedIcon from '@material-ui/icons/PlayCircleFilledRounded';
import PauseCircleFilledRoundedIcon from '@material-ui/icons/PauseCircleFilledRounded';
import SkipPreviousRoundedIcon from '@material-ui/icons/SkipPreviousRounded';
import SkipNextRoundedIcon from '@material-ui/icons/SkipNextRounded';

const Controls = () => {
  const { playerStatus: { status } } = useContext(SocketContext);

  const [isPlaying, setIsPlaying] = useState(false);
  const [hasPlaylist, setHasPlaylist] = useState(false);

  useEffect(() => {
    setIsPlaying(status?.state === 'play' ? true : false);
    setHasPlaylist(parseInt(status?.playlistlength) > 0);
  }, [status]);

  const play = () => {
    const folder = 'kita2';

    const method = hasPlaylist ? 'play' : 'playlistaddplay';
    const params = method === 'play' ? {} : { folder };

    setIsPlaying(true);
    execCommand('player', method, params);
  };

  const pause = () => {
    setIsPlaying(false);
    execCommand('player', 'pause');
  };

  const previous = () => {
    setIsPlaying(true);
    execCommand('player', 'prev');
  };

  const next = () => {
    setIsPlaying(true);
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
