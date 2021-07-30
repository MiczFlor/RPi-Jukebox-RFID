import React, { useContext, useEffect } from 'react';

import PlayerContext from '../../context/player/context';

import Grid from '@material-ui/core/Grid';
import IconButton from '@material-ui/core/IconButton';
import PlayCircleFilledRoundedIcon from '@material-ui/icons/PlayCircleFilledRounded';
import PauseCircleFilledRoundedIcon from '@material-ui/icons/PauseCircleFilledRounded';
import SkipPreviousRoundedIcon from '@material-ui/icons/SkipPreviousRounded';
import SkipNextRoundedIcon from '@material-ui/icons/SkipNextRounded';
import ShuffleRoundedIcon from '@material-ui/icons/ShuffleRounded';
import RepeatRoundedIcon from '@material-ui/icons/RepeatRounded';
import RepeatOneRoundedIcon from '@material-ui/icons/RepeatOneRounded';

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
    <Grid container direction="row" justify="center" alignItems="center">

      {/* Shuffle */}
      <IconButton
        aria-label="Shuffle"
        color={isShuffle ? 'primary' : undefined}
        onClick={toggleShuffle}
        >
        <ShuffleRoundedIcon style={{ fontSize: 20 }} />
      </IconButton>

      {/* Skip previous track */}
      <IconButton
        aria-label="Skip previous track"
        disabled={!songIsScheduled}
        onClick={previous}
      >
        <SkipPreviousRoundedIcon style={{ fontSize: 35 }} />
      </IconButton>

      {/* Play */}
      {
        !isPlaying &&
        <IconButton
          aria-label="Play"
          onClick={e => play()}
          disabled={!songIsScheduled}
        >
          <PlayCircleFilledRoundedIcon style={{ fontSize: 75 }} />
        </IconButton>
      }
      {
        isPlaying &&
        <IconButton
          aria-label="Pause"
          onClick={pause}
        >
          <PauseCircleFilledRoundedIcon style={{ fontSize: 75 }} />
        </IconButton>
      }

      {/* Skip next track */}
      <IconButton
        aria-label="Skip next track"
        disabled={!songIsScheduled}
        onClick={next}
      >
        <SkipNextRoundedIcon style={{ fontSize: 35 }} />
      </IconButton>

      {/* Repeat */}
      <IconButton
        aria-label="Repeat"
        color={isRepeat ? 'primary' : undefined}
        onClick={toggleRepeat}
      >
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
