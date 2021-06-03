import React, { useContext, useEffect, useState } from 'react';

import PlayerstatusContext from '../../context/playerstatus/context';
import useInterval from '../../hooks/useInterval';
import {
  positionToTime,
  timeToPosition,
  toHHMMSS,
} from '../utils';

import Grid from '@material-ui/core/Grid';
import Slider from '@material-ui/core/Slider';
import Typography from '@material-ui/core/Typography';

const SeekBar = () => {
  const { playerstatus, postJukeboxCommand } = useContext(PlayerstatusContext);

  const [isRunning, setIsRunning] = useState(playerstatus?.state === 'play' ? true : false);
  const [progress, setProgress] = useState(0);
  const [progressBarDelay] = useState(1000); // TODO: make it dynamic to have smoother progress
  const [timeElapsed, setTimeElapsed] = useState(parseFloat(playerstatus?.elapsed) || 0);
  const timeTotal = parseFloat(playerstatus?.duration) || 0;

  const updateTimeAndPosition = (newTime) => {
    setTimeElapsed(newTime);
    setProgress(timeToPosition(timeTotal, newTime));
  };

  // Handle seek events when sliding the progress bar
  const handleSeekToPosition = (event, newPosition) => {
    setIsRunning(false);
    updateTimeAndPosition(positionToTime(timeTotal, newPosition));
  };

  // Only send commend to backend when user committed to new position
  // We don't send it while seeking (too many useless requests)
  const playFromNewTime = () => {
    postJukeboxCommand('player', 'seek', { newTime: timeElapsed.toFixed(3) });
  };

  // Update progess bar every second
  useInterval(() => {
    updateTimeAndPosition(parseFloat(timeElapsed) + 1);
  }, isRunning ? progressBarDelay : null);

  useEffect(() => {
    setIsRunning(playerstatus?.state === 'play' ? true : false);
    updateTimeAndPosition(playerstatus?.elapsed);
  }, [playerstatus]);

  return (
    <>
      <Grid container direction="row" justify="space-between" alignItems="center">
        <Grid item>
          <Typography color="textSecondary">
            {toHHMMSS(parseInt(timeElapsed))}
          </Typography>
        </Grid>
        <Grid item>
          <Typography color="textSecondary">
            -{toHHMMSS(parseInt(timeTotal)-parseInt(timeElapsed))}
          </Typography>
        </Grid>
      </Grid>
      <Grid container>
        <Grid item xs>
          <Slider
            value={progress}
            onChange={handleSeekToPosition}
            onChangeCommitted={playFromNewTime}
            disabled={!playerstatus?.title}
            aria-labelledby="Song position"
          />
        </Grid>
      </Grid>
    </>
  );
};

export default SeekBar;
