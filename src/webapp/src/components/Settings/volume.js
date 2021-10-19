import React, { useContext, useState } from 'react';

import {
  Card,
  CardContent,
  CardHeader,
  Divider,
  Grid,
  Slider,
  Typography,
} from '@mui/material';
import PlayerContext from '../../context/player/context';

const marks = [5, 25, 50, 75, 100].map(
  (value) => ({ value, label: `${value}%` })
);

const SettingsVolume = () => {
  const {
    setMaxVolume,
    getMaxVolume,
  } = useContext(PlayerContext);

  const [volumeStep] = useState(5);
  const { maxVolume } = getMaxVolume;

  const updateMaxVolume = (event, newMaxVolume) => {
    setMaxVolume(newMaxVolume);
  }

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
              onChangeCommitted={updateMaxVolume}
              marks={marks}
              max={100}
              min={0}
              size="small"
              step={5}
              value={maxVolume}
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
