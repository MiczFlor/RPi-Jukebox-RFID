import React, { memo, useContext, useEffect } from 'react';
import { useTranslation } from 'react-i18next';

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
import request from '../../utils/request';

// TODO: Should be broken up in sub-modules
const Controls = () => {
  const { t } = useTranslation();
  const {
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

  const toggleShuffle = () => {
    request('shuffle', { option: 'toggle' });
  }

  const toggleRepeat = () => {
    request('repeat', { option: 'toggle' });
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

  const labelShuffle = () => (
    isShuffle
      ? t('player.controls.shuffle.disable')
      : t('player.controls.shuffle.enable')
  );

  const labelRepeat = () => {
    if (!isRepeat) return t('player.controls.repeat.enable');
    if (isRepeat && !isSingle) return t('player.controls.repeat.enable-single');
    if (isRepeat && isSingle) return t('player.controls.repeat.disable');
  };

  return (
    <Grid
      container
      alignItems="center"
      direction="row"
      flexWrap="nowrap"
      justifyContent="space-evenly"
    >

      {/* Shuffle */}
      <IconButton
        aria-label={labelShuffle()}
        color={isShuffle ? 'primary' : undefined}
        onClick={toggleShuffle}
        size="large"
        sx={iconStyles}
        title={labelShuffle()}
      >
        <ShuffleRoundedIcon style={{ fontSize: 22 }} />
      </IconButton>

      {/* Skip to previous song */}
      <IconButton
        aria-label={t('player.controls.prev_song')}
        disabled={!songIsScheduled}
        onClick={e => request('prev_song')}
        size="large"
        sx={iconStyles}
        title={t('player.controls.prev_song')}
      >
        <SkipPreviousRoundedIcon style={{ fontSize: 35 }} />
      </IconButton>

      {/* Play */}
      {!isPlaying &&
        <IconButton
          aria-label={t('player.controls.play')}
          onClick={e => request('play')}
          disabled={!songIsScheduled}
          size="large"
          sx={iconStyles}
          title={t('player.controls.play')}
        >
          <PlayCircleFilledRoundedIcon style={{ fontSize: 75 }} />
        </IconButton>
      }
      {/* Pause */}
      {isPlaying &&
        <IconButton
          aria-label={t('player.controls.pause')}
          onClick={e => request('pause')}
          size="large"
          sx={iconStyles}
          title={t('player.controls.pause')}
        >
          <PauseCircleFilledRoundedIcon style={{ fontSize: 75 }} />
        </IconButton>
      }

      {/* Skip to next song */}
      <IconButton
        aria-label={t('player.controls.next_song')}
        disabled={!songIsScheduled}
        onClick={e => request('next_song')}
        size="large"
        sx={iconStyles}
        title={t('player.controls.next_song')}
      >
        <SkipNextRoundedIcon style={{ fontSize: 35 }} />
      </IconButton>

      {/* Repeat */}
      <IconButton
        aria-label={labelRepeat()}
        color={isRepeat ? 'primary' : undefined}
        onClick={toggleRepeat}
        size="large"
        sx={iconStyles}
        title={labelRepeat()}
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

export default memo(Controls);
