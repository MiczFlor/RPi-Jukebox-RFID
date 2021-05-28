import React, { useContext, useEffect, useState } from 'react';

import SocketContext from '../../context/sockets/context';
import useInterval from '../../hooks/useInterval';

import { makeStyles } from '@material-ui/core/styles';
import Box from '@material-ui/core/Box';
import LinearProgress from '@material-ui/core/LinearProgress';
import Typography from '@material-ui/core/Typography';

const useStyles = makeStyles({
  bar: {
    transition: 'none',
  },
  divider: {
    marginLeft: '5px',
    marginRight: '5px',
  },
  dontBreak: {
    whiteSpace: 'nowrap',
    width: '100%',
    overflow: 'hidden',
    textOverflow: 'ellipsis',
  }
});

const Display = () => {
  const classes = useStyles();

  const { playerStatus: { status } } = useContext(SocketContext);

  const normalise = (duration, elapsed) => (elapsed) * 100 / (duration);

  const timeTotal = parseFloat(status?.duration) || 0;

  const [timeElapsed, setTimeElapsed] = useState(parseFloat(status?.elapsed) || 0);
  const [progress, setProgress] = useState(0);
  const [delay] = useState(1000);
  const [isRunning, setIsRunning] = useState(status?.state === 'play' ? true : false);

  useInterval(() => {
    const newTimeElapsed = timeElapsed + 1;
    setTimeElapsed(newTimeElapsed);
    setProgress(normalise(timeTotal, newTimeElapsed));
  }, isRunning ? delay : null);

  useEffect(() => {
    setIsRunning(status?.state === 'play' ? true : false);
    setTimeElapsed(parseFloat(status?.elapsed));
    setProgress(normalise(timeTotal, timeElapsed));
  }, [status])

  return (
    <Box my={4}>
      <Typography className={classes.dontBreak} component="h5" variant="h5">
        {status?.songid ? status?.title : 'No song in queue' }
      </Typography>
      <Typography className={classes.dontBreak} variant="subtitle1" color="textSecondary">
        {status?.songid && status?.artist }
        <span className={classes.divider}>&bull;</span>
        {status?.songid && status?.album }
      </Typography>

      <LinearProgress
        variant="determinate"
        value={progress}
        classes={{ bar: classes.bar }}
      />
    </Box>
  );
};

export default Display;
