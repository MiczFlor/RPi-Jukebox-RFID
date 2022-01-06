import React from 'react';

import {
  Card,
  CardContent,
  CardHeader,
  Divider,
  Grid,
  List,
} from '@mui/material';

import StatusBattery from './battery';
import StatusCpuTemp from './cpu-temp';
import StatusIpAddress from './ip-address';
import StatusVersion from './version';

const SettingsStatus = () => (
  <Card>
    <CardHeader title="System Status" />
    <Divider />
    <CardContent>
      <Grid container>
        <Grid item xs={12}>
          <List>
            <StatusVersion />
            <StatusBattery />
            <StatusIpAddress />
            <StatusCpuTemp />
          </List>
        </Grid>
      </Grid>
    </CardContent>
  </Card>
);

export default SettingsStatus;
