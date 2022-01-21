import React, { useContext, useEffect, useState } from 'react';
import { useTranslation } from 'react-i18next';

import Grid from '@mui/material/Grid';
import Slider from '@mui/material/Slider';
import Typography from '@mui/material/Typography';

import PubSubContext from '../../context/pubsub/context';
import { Counter } from '../general';
import {
  progressToTime,
  timeToProgress,
  toHHMMSS,
} from '../../utils/utils';
import request from '../../utils/request';

const SeekBar = () => {
  const { t } = useTranslation();
  const { state: { player_status } } = useContext(PubSubContext);

  const [isRunning, setIsRunning] = useState(player_status?.playing);
  const [isSeeking, setIsSeeking] = useState(false);
  const [progress, setProgress] = useState(0);
  const [timeElapsed, setTimeElapsed] = useState(parseFloat(player_status?.elapsed) || 0);
  const timeTotal = parseFloat(player_status?.duration) || 0;

  const updateTimeAndProgress = (newTime) => {
    setTimeElapsed(newTime);
    setProgress(timeToProgress(timeTotal, newTime));
  };

  // Handle seek events when sliding the progress bar
  const handleSeekToPosition = (event, newPosition) => {
    setIsSeeking(true);
    updateTimeAndProgress(progressToTime(timeTotal, newPosition));
  };

  // Only send command to backend when user committed to new position
  // We don't send it while seeking (too many useless requests)
  const playFromNewTime = () => {
    request('seek', { new_time: timeElapsed.toFixed(3) });
    setIsSeeking(false);
  };

  useEffect(() => {
    // Avoid updating time and progress when user is seeking to new
    // song position
    if (!isSeeking) {
      updateTimeAndProgress(player_status?.elapsed);
    }
  }, [player_status]);

  return <>
    <Grid container>
      <Grid item xs>
        <Slider
          aria-labelledby={t('player.seekbar.song-position')}
          disabled={!player_status?.title}
          onChange={handleSeekToPosition}
          onChangeCommitted={playFromNewTime}
          size="small"
          value={progress || 0}
        />
      </Grid>
    </Grid>
    <Grid
      alignItems="center"
      container
      direction="row"
      justifyContent="space-between"
      sx={ {
        marginTop: '-20px',
      }}
    >
      <Grid item>
        <Typography color="textSecondary">
          <Counter
            direction="up"
            paused={!isRunning}
            seconds={timeElapsed}
            end={timeTotal}
          />
        </Typography>
      </Grid>
      <Grid item>
        <Typography color="textSecondary">
          {toHHMMSS(parseInt(timeTotal))}
        </Typography>
      </Grid>
    </Grid>
  </>;
};

export default SeekBar;
