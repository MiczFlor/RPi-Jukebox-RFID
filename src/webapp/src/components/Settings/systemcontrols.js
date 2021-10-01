import React from 'react';

import {
  Card,
  CardContent,
  CardHeader,
  Divider,
  Grid,
} from '@mui/material';

import RebootDialog from './dialogs/reboot';
import ShutDownDialog from './dialogs/shutdown';

const SystemControls = () => {

  return (
    <Card>
      <CardHeader title="System Controls" />
      <Divider />
      <CardContent>
        <Grid container direction="row" justifyContent="space-around" alignItems="center">
          <Grid item>
            <RebootDialog />
          </Grid>
          <Grid item>
            <ShutDownDialog />
          </Grid>
        </Grid>
      </CardContent>
    </Card>
  );
};

export default SystemControls;
