import React, { useContext } from 'react';

import {
  Button,
  Card,
  CardContent,
  CardHeader,
  Divider,
  Grid,
} from '@material-ui/core';

import PlayerstatusContext from '../../context/playerstatus/context';

const SystemControls = () => {
  const { postJukeboxCommand  } = useContext(PlayerstatusContext);

  const reboot = () => {
    console.log('reboot');
    postJukeboxCommand('system', 'reboot', {});
  };

  const shutdown = () => {
    console.log('shutdown');
    postJukeboxCommand('system', 'shutdown', {});
  };

  return (
    <Card>
      <CardHeader title="System Controls" />
      <Divider />
      <CardContent>
        <Grid container direction="row" justify="space-around" alignItems="center">
          <Grid item>
            <Button variant="outlined" onClick={reboot}>Reboot</Button>
          </Grid>
          <Grid item>
            <Button variant="outlined" onClick={shutdown}>Shutdown</Button>
          </Grid>
        </Grid>
      </CardContent>
    </Card>
  );
};

export default SystemControls;
