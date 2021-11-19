import React from 'react';

import { Grid } from '@mui/material';

import SettingsAutoShutdown from './autoshutdown';
import SettingsSecondSwipe from './secondswipe';
import SystemControls from './systemcontrols';
import SettingsVolume from './volume';
import SettingsAutoHotspot from './autohotspot';

import { useTheme } from '@mui/material/styles';

const Settings = () => {
  const theme = useTheme();
  const spacer = { marginBottom: theme.spacing(1) }

  return (
    <Grid
      container
      direction="column"
      id="settings"
      sx={{ '& > .MuiGrid-item': spacer }}
    >
      <Grid item>
        <SystemControls />
      </Grid>
      <Grid item>
        <SettingsVolume />
      </Grid>
      <Grid item>
        <SettingsAutoShutdown />
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
