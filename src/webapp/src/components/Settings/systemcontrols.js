import React, { useContext } from 'react';

import {
  Card,
  CardContent,
  CardHeader,
  Divider,
  Grid,
} from '@material-ui/core';

import PlayerContext from '../../context/player/context';
import RebootDialog from './dialogs/reboot';
import ShutDownDialog from './dialogs/shutdown';

const SystemControls = () => {
  const { state: { postJukeboxCommand } } = useContext(PlayerContext);

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
