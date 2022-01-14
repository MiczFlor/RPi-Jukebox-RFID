import React from 'react';
import { useTranslation } from 'react-i18next';

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
  const { t } = useTranslation();

  return (
    <Card>
      <CardHeader title={t('settings.systemcontrols.title')} />
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
