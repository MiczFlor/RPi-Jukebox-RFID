import React, { useContext, useEffect, useState } from 'react';

import SocketContext from '../../context/sockets/context';
import { execCommand } from '../../sockets/emit';
import useInterval from '../../hooks/useInterval';

import Slider from '@material-ui/core/Slider';

const SeekBar = () => {
  const { playerStatus: { status } } = useContext(SocketContext);
  const timeTotal = parseFloat(status?.duration) || 0;

  const [timeElapsed, setTimeElapsed] = useState(parseFloat(status?.elapsed) || 0);
  const [progress, setProgress] = useState(0);
  const [delay] = useState(1000);
  const [isRunning, setIsRunning] = useState(status?.state === 'play' ? true : false);

  const timeToPosition = (duration, elapsed) => elapsed * 100 / duration;
  const positionToTime = (duration, position) => duration * position / 100;

  const updateTimeAndPosition = (newTime) => {
    setTimeElapsed(newTime);
    setProgress(timeToPosition(timeTotal, newTime));
  };

  // Handle seek events when sliding the progress bar
  const seekToPosition = (event, newPosition) => {
    setIsRunning(false);
    updateTimeAndPosition(positionToTime(timeTotal, newPosition));
  };

  // Only send commend to backend when user committed to new position
  // We don't send it while seeking (too many useless requests)
  const playFromNewTime = () => {
    execCommand('player', 'seek', { newTime: timeElapsed.toFixed(3) });
  };

  // Update progess bar every second
  useInterval(() => {
    updateTimeAndPosition(parseFloat(timeElapsed) + 1);
  }, isRunning ? delay : null);

  useEffect(() => {
    setIsRunning(status?.state === 'play' ? true : false);
    updateTimeAndPosition(status?.elapsed);
  }, [status]);

  return (
    <Slider
      value={progress}
      onChange={seekToPosition}
      onChangeCommitted={playFromNewTime}
      disabled={!status?.title}
      aria-labelledby="Song position"
    />
  );
};

export default SeekBar;
