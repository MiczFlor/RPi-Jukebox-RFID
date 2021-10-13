import React, { useState } from 'react';

import {
  Card,
  CardContent,
  CardHeader,
  Divider,
  Grid,
  Slider,
  Typography,
} from '@mui/material';

const marks = [5, 25, 50, 75, 100].map(
  (value) => ({ value, label: `${value}%` })
);

const SettingsVolume = () => {
  const {
    setMaxVolume,
  } = useContext(PlayerContext);

  const [volumeStep] = useState(1);
  const [maxVolume] = useState(75);
  const [isChangingMaxVolume, setIsChangingMaxVolume] = useState(false);
  const [_maxVolume, _setMaxVolume] = useState(0);

  const updateMaxVolume = () => {
    setMaxVolume(_maxVolume);
    // Delay the next command to avoid jumping slide control
    setTimeout(() => setIsChangingMaxVolume(false), 500);
  }

  const handleMaxVolumeChange = (event, newMaxVolume) => {
    setIsChangingMaxVolume(true);
    _setMaxVolume(newMaxVolume);
  }

  useEffect(() => {
    // Only trigger API when not dragging volume bar
    if (!isChangingMaxVolume) {
      _setMaxVolume(maxVolume);
    }
  }, [isChangingMaxVolume, maxVolume]);

  return (
    <Card>
      <CardHeader title="Volume" />
      <Divider />
      <CardContent>
        <Grid container direction="column">
          <Grid item>
            <Typography>Maximum Volume</Typography>
            <Slider
              defaultValue={maxVolume}
              onChange={handleMaxVolumeChange}
              onChangeCommitted={updateMaxVolume}
              marks={marks}
              max={100}
              min={0}
              size="small"
              step={1}
              value={typeof _maxVolume === 'number' ? _maxVolume : 75}
              valueLabelDisplay="auto"
            />
          </Grid>

          <Grid item>
            <Typography>Volume Steps</Typography>
            <Slider
              defaultValue={volumeStep}
              marks
              max={15}
              min={1}
              size="small"
              step={1}
              valueLabelDisplay="auto"
            />
          </Grid>
        </Grid>
      </CardContent>
    </Card>
  );
};

export default SettingsVolume;
