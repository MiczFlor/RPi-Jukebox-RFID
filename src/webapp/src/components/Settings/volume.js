import React, { useState } from 'react';

import {
  Card,
  CardContent,
  CardHeader,
  Divider,
  Grid,
  Slider,
  Typography,
} from '@material-ui/core';

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
              marks={marks}
              step={1}
              min={0}
              max={100}
              defaultValue={volumeMax}
            />
          </Grid>

          <Grid item>
            <Typography>Volume Steps</Typography>
            <Slider
              step={1}
              marks
              min={1}
              max={15}
              defaultValue={volumeStep}
            />
          </Grid>
        </Grid>
      </CardContent>
    </Card>
  );
};

export default SettingsVolume;
