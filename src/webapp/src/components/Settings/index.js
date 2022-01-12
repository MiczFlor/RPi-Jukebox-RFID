import React from 'react';

import { Grid } from '@mui/material';

import SettingsAutoHotspot from './autohotspot';
import SettingsSecondSwipe from './secondswipe';
import SettingsStatus from './status/index';
import SettingsTimers from './timers/index';
import SettingsVolume from './volume';
import SystemControls from './systemcontrols';

import { useTheme } from '@mui/material/styles';

const Settings = () => {
  const theme = useTheme();
  const spacer = { marginBottom: theme.spacing(1) }

  return (
    <Grid
      container
      direction="column"
      id="settings"
      sx={{
        '& > .MuiGrid-item': spacer,
        padding: '10px',
      }}
    >
      <Grid item>
        <SettingsStatus />
      </Grid>
      <Grid item>
        <SettingsTimers />
      </Grid>
      <Grid item>
        <SettingsVolume />
      </Grid>
      <Grid item>
        <SystemControls />
      </Grid>
      <Grid item>
        <SettingsSecondSwipe />
      </Grid>
      <Grid item>
        <SettingsAutoHotspot />
      </Grid>
    </Grid>
  );
};

export default Settings;
