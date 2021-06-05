import React from 'react';

import {
  Card,
  CardContent,
  CardHeader,
  Divider,
  Grid,
  NativeSelect,
  Typography,
} from '@material-ui/core';

const TIMESLOTS = [0, 2, 5, 10, 15, 20, 30, 45, 60, 120, 180, 240];

const options = TIMESLOTS.map(
  (value) => {
    if (value === 0) return { value, label: 'Off' };
    return { value, label: `${value} min` }
  }
);

const SettingsAutoShutdown = () => {
  return (
    <Card>
      <CardHeader title="Automatic Shutdown" />
      <Divider />
      <CardContent>
        <Grid container direction="column">
          <Grid container direction="row" justify="space-between" alignItems="center">
            <Grid item>
              <Typography>Stop Playout Timer</Typography>
            </Grid>
            <Grid item>
              <NativeSelect
                name="stopPlayoutTimer"
              >
                {options.map(({ value, label }) => (
                  <option key={value} value={value}>{label}</option>
                ))}
              </NativeSelect>
            </Grid>
          </Grid>

          <Grid container direction="row" justify="space-between" alignItems="center">
            <Grid item>
              <Typography>Shutdown Timer</Typography>
            </Grid>
            <Grid item>
              <NativeSelect
                name="shutdownTimer"
              >
                {options.map(({ value, label }) => (
                  <option key={value} value={value}>{label}</option>
                ))}
              </NativeSelect>
            </Grid>
          </Grid>

          <Grid container direction="row" justify="space-between" alignItems="center">
            <Grid item>
              <Typography>Idle Shutdown</Typography>
            </Grid>
            <Grid item>
              <NativeSelect
                name="shutdownTimer"
              >
                {options.map(({ value, label }) => (
                  <option key={value} value={value}>{label}</option>
                ))}
              </NativeSelect>
            </Grid>
          </Grid>
        </Grid>
      </CardContent>
    </Card>
  );
};

export default SettingsAutoShutdown;
