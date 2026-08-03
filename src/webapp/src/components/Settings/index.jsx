
import { Grid } from '@mui/material';

import SettingsAudio from './audio/index';
import SettingsAutoHotspot from './autohotspot';
import SettingsGeneral from './general';
import SettingsSecondSwipe from './secondswipe';
import SettingsStatus from './status/index';
import SettingsTimers from './timers/index';
import SystemControls from './systemcontrols';

import { useTheme } from '@mui/material/styles';

const Settings = () => {
  const theme = useTheme();
  const spacer = { marginBottom: theme.spacing(1) }

  return (
    <Grid
      container
      id="settings"
      sx={{
        '& > :not(:last-child)': spacer,
        flexDirection: 'column',
        padding: '10px',
      }}
    >
      <Grid>
        <SettingsStatus />
      </Grid>
      <Grid>
        <SettingsGeneral />
      </Grid>
      <Grid>
        <SettingsTimers />
      </Grid>
      <Grid>
        <SettingsAudio />
      </Grid>
      <Grid>
        <SystemControls />
      </Grid>
      <Grid>
        <SettingsSecondSwipe />
      </Grid>
      <Grid>
        <SettingsAutoHotspot />
      </Grid>
    </Grid>
  );
};

export default Settings;
