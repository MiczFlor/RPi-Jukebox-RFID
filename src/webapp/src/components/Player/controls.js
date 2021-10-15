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

  const iconStyles = { padding: '7px' };

  return (
    <Grid
      container
      alignItems="center"
      direction="row"
      flexWrap="nowrap"
      justifyContent="space-evenly"
      sx={{ margin: '7px 0' }}
    >

      {/* Shuffle */}
      <IconButton
        aria-label="Shuffle"
        color={isShuffle ? 'primary' : undefined}
        onClick={toggleShuffle}
        size="large"
        sx={iconStyles}
      >
        <ShuffleRoundedIcon style={{ fontSize: 22 }} />
      </IconButton>

      {/* Skip previous track */}
      <IconButton
        aria-label="Skip previous track"
        disabled={!songIsScheduled}
        onClick={previous}
        size="large"
        sx={iconStyles}
      >
        <SkipPreviousRoundedIcon style={{ fontSize: 35 }} />
      </IconButton>

      {/* Play */}
      {!isPlaying &&
        <IconButton
          aria-label="Play"
          onClick={e => play()}
          disabled={!songIsScheduled}
          size="large"
          sx={iconStyles}
        >
          <PlayCircleFilledRoundedIcon style={{ fontSize: 75 }} />
        </IconButton>
      }
      {/* Pause */}
      {isPlaying &&
        <IconButton
          aria-label="Pause"
          onClick={pause}
          size="large"
          sx={iconStyles}
        >
          <PauseCircleFilledRoundedIcon style={{ fontSize: 75 }} />
        </IconButton>
      }

      {/* Skip next track */}
      <IconButton
        aria-label="Skip next track"
        disabled={!songIsScheduled}
        onClick={next}
        size="large"
        sx={iconStyles}
      >
        <SkipNextRoundedIcon style={{ fontSize: 35 }} />
      </IconButton>

      {/* Repeat */}
      <IconButton
        aria-label="Repeat"
        color={isRepeat ? 'primary' : undefined}
        onClick={toggleRepeat}
        size="large"
        sx={iconStyles}
      >
        {
          !isSingle &&
          <RepeatRoundedIcon style={{ fontSize: 22 }} />
        }
        {
          isSingle &&
          <RepeatOneRoundedIcon style={{ fontSize: 22 }} />
        }
      </IconButton>

    </Grid>
  );
};

export default Controls;
