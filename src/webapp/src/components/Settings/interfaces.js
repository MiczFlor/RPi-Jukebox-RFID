import React from 'react';

import {
  Card,
  CardContent,
  CardHeader,
  Divider,
  Grid,
  Switch,
  Typography,
} from '@material-ui/core';

const SettingsInterface = () => {
  return (
    <Card>
      <CardHeader title="Externel Interfaces" />
      <Divider />
      <CardContent>
        <Grid container direction="column">
          <Grid container direction="row" justify="space-between" alignItems="center">
            <Grid item>
              <Typography>Enable RFID Reader</Typography>
            </Grid>
            <Grid item>
              <Switch
                checked={true}
                name="rfidReaderEnabled"
                inputProps={{ 'aria-label': 'Enable RFID Reader' }}
              />
            </Grid>
          </Grid>

          <Grid container direction="row" justify="space-between" alignItems="center">
            <Grid item>
              <Typography>Enable GPIO Buttons</Typography>
            </Grid>
            <Grid item>
              <Switch
                checked={true}
                name="gpioButtonsEnabled"
                inputProps={{ 'aria-label': 'Enable GPIO Buttons' }}
              />
            </Grid>
          </Grid>
        </Grid>
      </CardContent>
    </Card>
  );
};

export default SettingsInterface;
