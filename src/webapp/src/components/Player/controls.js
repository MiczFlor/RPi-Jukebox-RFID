import React, { useContext, useEffect } from 'react';

import Grid from '@mui/material/Grid';
import IconButton from '@mui/material/IconButton';
import PlayCircleFilledRoundedIcon from '@mui/icons-material/PlayCircleFilledRounded';
import PauseCircleFilledRoundedIcon from '@mui/icons-material/PauseCircleFilledRounded';
import SkipPreviousRoundedIcon from '@mui/icons-material/SkipPreviousRounded';
import SkipNextRoundedIcon from '@mui/icons-material/SkipNextRounded';
import ShuffleRoundedIcon from '@mui/icons-material/ShuffleRounded';
import RepeatRoundedIcon from '@mui/icons-material/RepeatRounded';
import RepeatOneRoundedIcon from '@mui/icons-material/RepeatOneRounded';

import PlayerContext from '../../context/player/context';

const Controls = () => {
  const {
    play,
    pause,
    previous,
    next,
    shuffle,
    repeat,
    state,
    setState,
  } = useContext(PlayerContext);

  const {
    isPlaying,
    playerstatus,
    isShuffle,
    isRepeat,
    isSingle,
    songIsScheduled
  } = state;

  const toggleShuffle = (event) => {
    shuffle(!isShuffle);
  }

  const toggleRepeat = (event) => {
    repeat(isRepeat, isSingle);
  }

  useEffect(() => {
    setState({
      ...state,
      isPlaying: playerstatus?.state === 'play' ? true : false,
      songIsScheduled: playerstatus?.songid ? true : false,
      isShuffle: playerstatus?.random === '1' ? true : false,
      isRepeat: playerstatus?.repeat === '1' ? true : false,
      isSingle: playerstatus?.single === '1' ? true : false,
    });
  }, [playerstatus]);

  return (
    <Grid container direction="row" justifyContent="center" alignItems="center">

      {/* Shuffle */}
      <IconButton
        aria-label="Shuffle"
        color={isShuffle ? 'primary' : undefined}
        onClick={toggleShuffle}
        size="large">
        <ShuffleRoundedIcon style={{ fontSize: 20 }} />
      </IconButton>

      {/* Skip previous track */}
      <IconButton
        aria-label="Skip previous track"
        disabled={!songIsScheduled}
        onClick={previous}
        size="large">
        <SkipPreviousRoundedIcon style={{ fontSize: 35 }} />
      </IconButton>

      {/* Play */}
      {
        !isPlaying &&
        <IconButton
          aria-label="Play"
          onClick={e => play()}
          disabled={!songIsScheduled}
          size="large">
          <PlayCircleFilledRoundedIcon style={{ fontSize: 75 }} />
        </IconButton>
      }
      {
        isPlaying &&
        <IconButton aria-label="Pause" onClick={pause} size="large">
          <PauseCircleFilledRoundedIcon style={{ fontSize: 75 }} />
        </IconButton>
      }

      {/* Skip next track */}
      <IconButton
        aria-label="Skip next track"
        disabled={!songIsScheduled}
        onClick={next}
        size="large">
        <SkipNextRoundedIcon style={{ fontSize: 35 }} />
      </IconButton>

      {/* Repeat */}
      <IconButton
        aria-label="Repeat"
        color={isRepeat ? 'primary' : undefined}
        onClick={toggleRepeat}
        size="large">
        {
          !isSingle &&
          <RepeatRoundedIcon style={{ fontSize: 20 }} />
        }
        {
          isSingle &&
          <RepeatOneRoundedIcon style={{ fontSize: 25 }} />
        }
      </IconButton>

    </Grid>
  );
};

export default Controls;
