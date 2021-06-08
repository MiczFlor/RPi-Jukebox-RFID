import React, { useContext, useEffect, useState } from 'react';

import PlayerContext from '../../context/player/context';

import Grid from '@material-ui/core/Grid';
import IconButton from '@material-ui/core/IconButton';
import PlayCircleFilledRoundedIcon from '@material-ui/icons/PlayCircleFilledRounded';
import PauseCircleFilledRoundedIcon from '@material-ui/icons/PauseCircleFilledRounded';
import SkipPreviousRoundedIcon from '@material-ui/icons/SkipPreviousRounded';
import SkipNextRoundedIcon from '@material-ui/icons/SkipNextRounded';

const Controls = () => {
  const {
    play,
    pause,
    previous,
    next,
    state,
    setState,
  } = useContext(PlayerContext);

  const { isPlaying, playerstatus } = state;

  useEffect(() => {
    setState({ ...state, isPlaying: playerstatus?.state === 'play' ? true : false });
  }, [playerstatus]);

  return (
    <Grid container direction="row" justify="center" alignItems="center">
      <IconButton aria-label="Skip previous track" onClick={previous}>
        <SkipPreviousRoundedIcon style={{ fontSize: 35 }} />
      </IconButton>
      {
        !isPlaying &&
        <IconButton aria-label="Play" onClick={e => play()}>
          <PlayCircleFilledRoundedIcon style={{ fontSize: 75 }} />
        </IconButton>
      }
      {
        isPlaying &&
        <IconButton aria-label="Pause" onClick={pause}>
          <PauseCircleFilledRoundedIcon style={{ fontSize: 75 }} />
        </IconButton>
      }
      <IconButton aria-label="Skip next track" onClick={next}>
        <SkipNextRoundedIcon style={{ fontSize: 35 }} />
      </IconButton>
    </Grid>
  );
};

export default Controls;
