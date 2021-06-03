import React, { useContext, useEffect, useState } from 'react';

import PlayerstatusContext from '../../context/playerstatus/context';

import Grid from '@material-ui/core/Grid';
import IconButton from '@material-ui/core/IconButton';
import PlayCircleFilledRoundedIcon from '@material-ui/icons/PlayCircleFilledRounded';
import PauseCircleFilledRoundedIcon from '@material-ui/icons/PauseCircleFilledRounded';
import SkipPreviousRoundedIcon from '@material-ui/icons/SkipPreviousRounded';
import SkipNextRoundedIcon from '@material-ui/icons/SkipNextRounded';

const Controls = () => {
  const { playerstatus, postJukeboxCommand  } = useContext(PlayerstatusContext);

  const [isPlaying, setIsPlaying] = useState(false);
  const [hasPlaylist, setHasPlaylist] = useState(false);

  const play = () => {
    const folder = 'kita2';

    const method = hasPlaylist ? 'play' : 'playlistaddplay';
    const kwargs = method === 'play' ? {} : { folder };

    setIsPlaying(true);
    postJukeboxCommand('player', method, kwargs);
  };

  const pause = () => {
    setIsPlaying(false);
    postJukeboxCommand('player', 'pause');
  };

  const previous = () => {
    setIsPlaying(true);
    postJukeboxCommand('player', 'prev');
  };

  const next = () => {
    setIsPlaying(true);
    postJukeboxCommand('player', 'next');
  };

  useEffect(() => {
    setIsPlaying(playerstatus?.state === 'play' ? true : false);
    setHasPlaylist(parseInt(playerstatus?.playlistlength) > 0);
  }, [playerstatus]);

  return (
    <Grid container direction="row" justify="center" alignItems="center">
      <IconButton aria-label="Skip previous track" onClick={previous}>
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
      <IconButton aria-label="Skip next track" onClick={next}>
        <SkipNextRoundedIcon style={{ fontSize: 35 }} />
      </IconButton>
    </Grid>
  );
};

export default Controls;
