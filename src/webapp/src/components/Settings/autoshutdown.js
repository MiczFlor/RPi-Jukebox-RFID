import React from 'react';

import {
  Card,
  CardContent,
  CardHeader,
  Divider,
  Grid,
  InputLabel,
  NativeSelect,
} from '@mui/material';

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
      <CardHeader
        title="Automatic Shutdown"
        subheader="🚧 This feature is not yet enabled."
      />
      <Divider />
      <CardContent>
        <Grid container direction="column">
          <Grid container direction="row" justifyContent="space-between" alignItems="center">
            <Grid item>
              <InputLabel htmlFor="stopPlayoutTimer">Stop Playout Timer</InputLabel>
            </Grid>
            <Grid item>
              <NativeSelect
                disabled={true}
                id="stopPlayoutTimer"
                name="stopPlayoutTimer"
              >
                {options.map(({ value, label }) => (
                  <option key={value} value={value}>{label}</option>
                ))}
              </NativeSelect>
            </Grid>
          </Grid>

          <Grid container direction="row" justifyContent="space-between" alignItems="center">
            <Grid item>
              <InputLabel htmlFor="shutdownTimer">Shutdown Timer</InputLabel>
            </Grid>
            <Grid item>
              <NativeSelect
                disabled={true}
                id="shutdownTimer"
                name="shutdownTimer"
              >
                {options.map(({ value, label }) => (
                  <option key={value} value={value}>{label}</option>
                ))}
              </NativeSelect>
            </Grid>
          </Grid>

          <Grid container direction="row" justifyContent="space-between" alignItems="center">
            <Grid item>
              <InputLabel htmlFor="shutdownTimer">Idle Shutdown</InputLabel>
            </Grid>
            <Grid item>
              <NativeSelect
                disabled={true}
                id="shutdownTimer"
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
