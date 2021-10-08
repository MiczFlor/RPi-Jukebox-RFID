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
  const [volumeStep] = useState(1);
  const [volumeMax] = useState(75);

  return (
    <Card>
      <CardHeader title="Volume" />
      <Divider />
      <CardContent>
        <Grid container direction="column">
          <Grid item>
            <Typography>Maximum Volume</Typography>
            <Slider
              defaultValue={volumeMax}
              marks={marks}
              max={100}
              min={0}
              size="small"
              step={1}
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
